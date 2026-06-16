"""Shadow-clone compositing — the visual payload of Kage Bunshin.

Segments the largest person in the frame with a stock YOLOv8 segmentation model, cuts
them out using the mask, and composites translucent copies at horizontal offsets so the
caster appears flanked by clones. A brief smoke puff plays as the clones appear.

The segmentation model is loaded lazily and only invoked while a jutsu is active, so it
costs nothing during normal detection on a CPU-only machine.
"""

import time

import cv2
import numpy as np
from ultralytics import YOLO

from . import config
from .clone_geometry import clone_paste_rect

_PERSON_CLASS = 0  # COCO class id for "person"


class CloneEffect:
    def __init__(self, seg_model_path=None, time_fn=time.monotonic):
        self._seg_model_path = str(seg_model_path or config.SEG_MODEL_PATH)
        self._time_fn = time_fn
        self._model = None
        self._smoke_started_at = None

    def _ensure_model(self):
        if self._model is None:
            self._model = YOLO(self._seg_model_path)
        return self._model

    def _largest_person(self, frame):
        """Return `(bbox, mask)` for the biggest detected person, or `None`.

        `bbox` is an int `(x1, y1, x2, y2)`; `mask` is a float32 array the size of `frame`
        with values in [0, 1].
        """
        results = self._ensure_model()(frame, classes=[_PERSON_CLASS], verbose=False)
        result = results[0]
        if result.masks is None or len(result.boxes) == 0:
            return None

        boxes = result.boxes.xyxy.cpu().numpy()
        areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
        idx = int(areas.argmax())

        frame_h, frame_w = frame.shape[:2]
        mask = result.masks.data[idx].cpu().numpy().astype(np.float32)
        mask = cv2.resize(mask, (frame_w, frame_h), interpolation=cv2.INTER_NEAREST)

        x1, y1, x2, y2 = boxes[idx].astype(int)
        bbox = (max(0, x1), max(0, y1), min(frame_w, x2), min(frame_h, y2))
        return bbox, mask

    def render(self, frame, just_cast=False):
        """Composite clones onto `frame` in place and return it.

        Pass `just_cast=True` on the frame the cast fires to (re)start the smoke puff.
        """
        if just_cast:
            self._smoke_started_at = self._time_fn()

        found = self._largest_person(frame)
        if found is None:
            return frame
        bbox, mask = found

        original = frame.copy()
        x1, y1, x2, y2 = bbox
        cutout_bgr = original[y1:y2, x1:x2]
        cutout_alpha = mask[y1:y2, x1:x2]

        offsets = config.CLONE_OFFSETS[: config.CLONE_COUNT]
        frame_h, frame_w = frame.shape[:2]
        for offset_ratio in offsets:
            rect = clone_paste_rect(frame_w, frame_h, bbox, offset_ratio)
            if rect is None:
                continue
            dx1, dy1, dx2, dy2, sx1, sy1, sx2, sy2 = rect
            src = cutout_bgr[sy1:sy2, sx1:sx2].astype(np.float32)
            alpha = (cutout_alpha[sy1:sy2, sx1:sx2] * config.CLONE_ALPHA)[..., None]
            dst = frame[dy1:dy2, dx1:dx2].astype(np.float32)
            frame[dy1:dy2, dx1:dx2] = (src * alpha + dst * (1.0 - alpha)).astype(np.uint8)

        self._draw_smoke(frame, bbox, offsets)
        return frame

    def _draw_smoke(self, frame, bbox, offsets):
        if self._smoke_started_at is None:
            return
        elapsed = self._time_fn() - self._smoke_started_at
        if elapsed > config.SMOKE_DURATION:
            return

        x1, y1, x2, y2 = bbox
        person_w = x2 - x1
        progress = elapsed / config.SMOKE_DURATION
        radius = int(person_w * (0.4 + 0.6 * progress))
        intensity = 1.0 - progress  # fades out as it expands

        overlay = frame.copy()
        center_y = (y1 + y2) // 2
        for offset_ratio in offsets:
            cx = int(x1 + person_w / 2 + offset_ratio * person_w)
            cv2.circle(overlay, (cx, center_y), radius, (220, 220, 220), thickness=-1)
        cv2.addWeighted(overlay, intensity, frame, 1.0 - intensity, 0, frame)
