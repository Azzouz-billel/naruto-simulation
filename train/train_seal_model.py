"""Train the YOLOv8 seal detector. Run on a GPU (e.g. Google Colab) — CPU is impractical.

    python train/train_seal_model.py --data path/to/data.yaml --epochs 50

On completion the best weights are copied to cv/models/seal_detector.pt, which is what
app.py loads at runtime.
"""

import argparse
import shutil
from pathlib import Path

from ultralytics import YOLO

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEST = PROJECT_ROOT / "models" / "seal_detector.pt"


def parse_args():
    parser = argparse.ArgumentParser(description="Train the Naruto seal detector.")
    parser.add_argument("--data", required=True, help="Path to the dataset data.yaml.")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--model", default="yolov8n.pt", help="Base weights to fine-tune.")
    return parser.parse_args()


def main():
    args = parse_args()
    model = YOLO(args.model)
    model.train(data=args.data, epochs=args.epochs, imgsz=args.imgsz)

    best = Path(model.trainer.save_dir) / "weights" / "best.pt"
    DEST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(best, DEST)
    print(f"Saved {best} -> {DEST}")


if __name__ == "__main__":
    main()
