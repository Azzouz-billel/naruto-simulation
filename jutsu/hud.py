"""On-screen text overlays. Matches the purple cv2.putText style of the original test.py."""

import cv2

_FONT = cv2.FONT_HERSHEY_SIMPLEX
_PURPLE = (255, 0, 255)
_WHITE = (255, 255, 255)


def draw_seal_label(frame, detection):
    """Show the current seal read at the top-left, e.g. `Seal: clone (0.82)`."""
    if detection is None:
        text = "Seal: -"
    else:
        name, conf = detection
        text = f"Seal: {name} ({conf:.2f})"
    cv2.putText(frame, text, (15, 35), _FONT, 0.9, _PURPLE, 2)


def draw_jutsu_banner(frame, text, clone_count):
    """Centered jutsu banner plus a clone counter, shown while the jutsu is active."""
    height, width = frame.shape[:2]
    (text_w, _), _ = cv2.getTextSize(text, _FONT, 1.2, 3)
    x = (width - text_w) // 2
    y = height - 40
    cv2.putText(frame, text, (x, y), _FONT, 1.2, _WHITE, 5)   # outline for legibility
    cv2.putText(frame, text, (x, y), _FONT, 1.2, _PURPLE, 3)
    cv2.putText(frame, f"Clones: {clone_count}", (15, height - 20), _FONT, 0.7, _PURPLE, 2)
