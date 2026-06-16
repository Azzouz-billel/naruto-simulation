"""Hand-seal recognition — wraps the custom-trained YOLOv8 detector.

Reports only the single most-confident seal per frame; the confidence gating and
temporal smoothing live in CastStabilizer, keeping this class a thin model wrapper.
"""

from pathlib import Path

from ultralytics import YOLO

from . import config


class SealDetector:
    def __init__(self, model_path=None):
        path = Path(model_path or config.SEAL_MODEL_PATH)
        if not path.exists():
            raise FileNotFoundError(
                f"Seal model not found at {path}. Train it first (see train/train_seal_model.py "
                "on Colab) and place best.pt there, or run app.py with --no-detector to test the "
                "clone effect via the manual cast key."
            )
        self._model = YOLO(str(path))

    def update(self, frame):
        """Return the highest-confidence seal as `(class_name, confidence)`, or `None`."""
        result = self._model(frame, verbose=False)[0]
        if len(result.boxes) == 0:
            return None

        confs = result.boxes.conf.cpu().numpy()
        idx = int(confs.argmax())
        class_id = int(result.boxes.cls[idx])
        return self._model.names[class_id], float(confs[idx])
