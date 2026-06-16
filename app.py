"""Live Naruto jutsu detector.

Form the trigger hand seal in front of the webcam; once it holds steady, the app casts
Kage Bunshin no Jutsu and composites shadow clones of you into the frame.

    python app.py                 # full pipeline (needs models/seal_detector.pt)
    python app.py --no-detector   # skip the seal model; cast manually with the 'c' key
    python app.py --camera 1      # pick a different webcam index

Keys: 'c' cast manually, 'q' quit.
"""

import argparse

import cv2

from jutsu import config, hud
from jutsu.cast_stabilizer import CastStabilizer
from jutsu.clone_effect import CloneEffect
from jutsu.seal_detector import SealDetector

_JUTSU_NAME = "Kage Bunshin no Jutsu!"


def parse_args():
    parser = argparse.ArgumentParser(description="Live Naruto jutsu detector.")
    parser.add_argument("--camera", type=int, default=0, help="Webcam index (default 0).")
    parser.add_argument(
        "--no-detector",
        action="store_true",
        help="Skip the seal model; cast manually with the 'c' key.",
    )
    return parser.parse_args()


def run(camera_index, use_detector):
    detector = None if not use_detector else SealDetector()
    stabilizer = CastStabilizer(
        trigger_seal=config.TRIGGER_SEAL,
        conf_threshold=config.CONF_THRESHOLD,
        consecutive_frames=config.CONSECUTIVE_FRAMES,
        jutsu_duration=config.JUTSU_DURATION,
    )
    effect = CloneEffect()

    capture = cv2.VideoCapture(camera_index)
    if not capture.isOpened():
        raise RuntimeError(f"Could not open camera {camera_index}.")

    cv2.namedWindow("Jutsu", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Jutsu", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    try:
        while True:
            success, frame = capture.read()
            if not success or frame is None:
                print("Failed to read from camera.")
                break

            detection = detector.update(frame) if detector else None
            cast_fired = stabilizer.update(detection)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("c"):
                cast_fired = stabilizer.force_cast()

            if stabilizer.is_active():
                effect.render(frame, just_cast=cast_fired)
                hud.draw_jutsu_banner(frame, _JUTSU_NAME, config.CLONE_COUNT)

            hud.draw_seal_label(frame, detection)
            cv2.imshow("Jutsu", frame)

            if key == ord("q"):
                break
    finally:
        capture.release()
        cv2.destroyAllWindows()


def main():
    args = parse_args()
    run(camera_index=args.camera, use_detector=not args.no_detector)


if __name__ == "__main__":
    main()
