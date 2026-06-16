"""Tunable settings for the jutsu detector.

Single source of truth for thresholds and effect parameters so the rest of the
package stays free of magic numbers.
"""

from pathlib import Path

# Repo-relative paths. `jutsu/` sits one level under the project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SEAL_MODEL_PATH = PROJECT_ROOT / "models" / "seal_detector.pt"
SEG_MODEL_PATH = PROJECT_ROOT / "yolov8n-seg.pt"  # auto-downloaded by ultralytics if absent

# Which seal triggers the jutsu. Must exactly match a class name in the trained model.
# The trained model has the 12 zodiac seals (no clone-cross), so we use the iconic "ram"
# release seal. Swap for any of: bird, boar, dog, dragon, hare, horse, monkey, ox, ram,
# rat, snake, tiger.
TRIGGER_SEAL = "dragon"

# Detection / cast gating.
CONF_THRESHOLD = 0.50       # minimum seal confidence to count toward a cast
CONSECUTIVE_FRAMES = 10     # frames the trigger seal must hold before casting (~0.3s @ 30fps)
JUTSU_DURATION = 5.0        # seconds the clone effect stays active after a cast

# Clone effect.
CLONE_COUNT = 4             # number of shadow clones composited around the real person
CLONE_OFFSETS = (-1.0, -0.5, 0.5, 1.0)  # horizontal offsets as multiples of person width
CLONE_ALPHA = 0.85          # opacity of composited clones (slightly translucent reads as "clone")
SMOKE_DURATION = 0.6        # seconds the appearance smoke-puff is shown
