"""Download a Naruto hand-sign dataset from Roboflow in YOLOv8 format.

Requires a free Roboflow account + API key:

    export ROBOFLOW_API_KEY=xxxxxxxx
    python train/download_dataset.py

Edit WORKSPACE / PROJECT / VERSION below to match the dataset you picked on Roboflow
Universe, then inspect the printed data.yaml class list and set TRIGGER_SEAL in
jutsu/config.py to whichever class is the Kage Bunshin clone-cross (or "ram" if absent).

Manual fallback (no API key): open the dataset page on Roboflow Universe, choose
"Download Dataset" -> format "YOLOv8" -> "download zip", unzip it under cv/datasets/, and
pass its data.yaml to train/train_seal_model.py with --data.
"""

import os

from roboflow import Roboflow

# Default points at a public ~6k-image Naruto hand-sign dataset.
WORKSPACE = "vgu-aeaes"
PROJECT = "naruto-hand-sign"
VERSION = 1


def main():
    api_key = os.environ.get("ROBOFLOW_API_KEY")
    if not api_key:
        raise SystemExit(
            "Set ROBOFLOW_API_KEY first (or use the manual download fallback in this "
            "module's docstring)."
        )

    rf = Roboflow(api_key=api_key)
    project = rf.workspace(WORKSPACE).project(PROJECT)
    dataset = project.version(VERSION).download("yolov8")

    print(f"Downloaded to: {dataset.location}")
    print(f"Pass this to training: --data {dataset.location}/data.yaml")
    print("Now open that data.yaml and set jutsu/config.py:TRIGGER_SEAL to the clone seal.")


if __name__ == "__main__":
    main()
