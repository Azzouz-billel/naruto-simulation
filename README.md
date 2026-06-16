# Naruto Jutsu Detector 🥷

Perform a Naruto hand seal in front of your webcam and the app casts **Kage Bunshin no Jutsu** —
it recognizes the seal in real time, segments you out of the frame, and composites **shadow clones**
of you with a puff of smoke.

Built with **YOLOv8** (Ultralytics) and **OpenCV**. Two models run the show: a custom-trained seal
detector recognizes the hand sign, and a stock segmentation model cuts you out so your clones can be
pasted beside you.

https://user-images.githubusercontent.com/placeholder/demo.gif  <!-- replace with your own demo gif -->

---

## How it works

```
webcam ─▶ SealDetector ─▶ CastStabilizer ─▶ CloneEffect ─▶ HUD ─▶ fullscreen window
          (which seal?)    (held long enough?)  (segment + clone)   (labels/banner)
```

| Stage | Module | Job |
|-------|--------|-----|
| Recognize the seal | [`jutsu/seal_detector.py`](jutsu/seal_detector.py) | Custom YOLOv8 model → highest-confidence seal per frame |
| Avoid flicker | [`jutsu/cast_stabilizer.py`](jutsu/cast_stabilizer.py) | Fires a cast only after the trigger seal holds steady for N frames; keeps the jutsu active for a few seconds |
| The effect | [`jutsu/clone_effect.py`](jutsu/clone_effect.py) | Segments the person (`yolov8n-seg`), cuts an RGBA cutout, composites clones at horizontal offsets + smoke puff |
| Placement math | [`jutsu/clone_geometry.py`](jutsu/clone_geometry.py) | Pure, unit-tested clipping logic for clone positions |
| Overlays | [`jutsu/hud.py`](jutsu/hud.py) | Seal label + "Kage Bunshin no Jutsu!" banner |
| Settings | [`jutsu/config.py`](jutsu/config.py) | All tunables in one place |

To keep things fast on CPU, the segmentation model only runs **while a jutsu is active** — normal
detection is just the lightweight seal model.

---

## Requirements

- Python 3.12
- A webcam
- ~1 GB disk for model weights

Python dependencies are in [`requirements.txt`](requirements.txt) (`ultralytics`, `opencv-python`,
`numpy`, `roboflow`, `pytest`).

---

## Installation

```bash
git clone <your-repo-url>
cd cv

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

The `yolov8n-seg.pt` segmentation weights download automatically on first run.

---

## The seal model (you train this)

The trained seal detector (`models/seal_detector.pt`) is **not** included in the repo — it's
gitignored because of its size. You have two options:

**Train your own (recommended)**
1. Open [`train/train_on_colab.ipynb`](train/train_on_colab.ipynb) in Google Colab.
2. Set the runtime to a **T4 GPU**, paste your Roboflow API key, and *Run all*.
3. Download the resulting `best.pt` and place it at `models/seal_detector.pt`.

The default dataset trains the **12 zodiac seals**: `bird, boar, dog, dragon, hare, horse, monkey,
ox, ram, rat, snake, tiger`. Note the class names — you'll point `TRIGGER_SEAL` at one of them.

**Skip the model for now** — you can still see the clone effect (see `--no-detector` below).

---

## Running it

```bash
python app.py                 # full experience (needs models/seal_detector.pt)
python app.py --no-detector   # no seal model; cast manually to test the effect
python app.py --camera 1      # use a different webcam index
```

The window opens **fullscreen**.

| Key | Action |
|-----|--------|
| `c` | Cast manually (force the jutsu) |
| `q` | Quit |

Form the trigger seal (default: **bird**) and hold it steady for ~⅓ second. The top-left HUD shows
the live seal read and its confidence, so you can watch it cross the threshold.

---

## Configuration

Everything tunable lives in [`jutsu/config.py`](jutsu/config.py):

| Setting | Default | Meaning |
|---------|---------|---------|
| `TRIGGER_SEAL` | `"bird"` | Which seal casts the jutsu (must match a model class name) |
| `CONF_THRESHOLD` | `0.50` | Minimum confidence for a detection to count |
| `CONSECUTIVE_FRAMES` | `10` | Frames the seal must hold before casting (~0.3 s @ 30 fps) |
| `JUTSU_DURATION` | `5.0` | Seconds the clone effect stays active |
| `CLONE_COUNT` | `4` | Number of shadow clones |
| `CLONE_OFFSETS` | `(-1.0, -0.5, 0.5, 1.0)` | Clone positions, in multiples of body width |
| `CLONE_ALPHA` | `0.85` | Clone opacity |
| `SMOKE_DURATION` | `0.6` | Length of the appearance smoke puff |

---

## Testing

The pure logic (cast timing + clone geometry) is unit-tested:

```bash
python -m pytest tests/ -q
```

The live camera loop and model accuracy are verified by hand.

---

## Project structure

```
cv/
├── app.py                     # main webcam loop
├── jutsu/
│   ├── seal_detector.py       # YOLOv8 seal recognition
│   ├── cast_stabilizer.py     # temporal cast gating
│   ├── clone_effect.py        # segmentation + clone compositing
│   ├── clone_geometry.py      # pure clone-placement math
│   ├── hud.py                 # on-screen overlays
│   └── config.py              # all tunables
├── train/
│   ├── train_on_colab.ipynb   # GPU training notebook
│   ├── download_dataset.py    # Roboflow dataset download
│   └── train_seal_model.py    # local/Colab training script
├── tests/
│   ├── test_cast_stabilizer.py
│   └── test_clone_geometry.py
├── models/                    # seal_detector.pt goes here (gitignored)
└── requirements.txt
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Could not open camera 0` | Close other apps using the webcam, or try `--camera 1` |
| `Seal model not found` | Train the model and place it at `models/seal_detector.pt`, or run `--no-detector` |
| Seal never triggers | Lower `CONF_THRESHOLD` (e.g. `0.4`); watch the HUD confidence |
| Casts by accident | Raise `CONF_THRESHOLD` or `CONSECUTIVE_FRAMES` |
| Poor accuracy on your hands | The public dataset wasn't trained on you — collect your own seal photos and fine-tune |

---

## Credits & disclaimer

Hand-seal datasets come from [Roboflow Universe](https://universe.roboflow.com). Detection and
segmentation use [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics). Naruto and its
jutsu are property of Masashi Kishimoto / Shueisha — this is a non-commercial fan project for
learning computer vision.
