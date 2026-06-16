"""Temporal gating for jutsu casting — pure logic, no OpenCV.

A raw per-frame seal detection flickers: it drops out for a frame, dips below the
confidence threshold, or briefly misfires. Casting straight off a single frame would
be jittery and trigger on accidental hand positions. CastStabilizer requires the
trigger seal to hold for a run of consecutive frames before it fires a one-shot cast,
then keeps the jutsu "active" for a fixed duration.
"""

import time


class CastStabilizer:
    def __init__(
        self,
        trigger_seal,
        conf_threshold,
        consecutive_frames,
        jutsu_duration,
        time_fn=time.monotonic,
    ):
        self._trigger_seal = trigger_seal
        self._conf_threshold = conf_threshold
        self._consecutive_frames = consecutive_frames
        self._jutsu_duration = jutsu_duration
        self._time_fn = time_fn
        self._streak = 0
        self._active_until = None

    def update(self, detection):
        """Advance one frame.

        `detection` is `(seal_name, confidence)` or `None`. Returns `True` only on the
        frame a cast fires. While a jutsu is already active no new cast can fire and the
        streak is held at zero, so holding the seal through the effect does not re-trigger.
        """
        now = self._time_fn()
        if self.is_active(now):
            self._streak = 0
            return False

        is_trigger = (
            detection is not None
            and detection[0] == self._trigger_seal
            and detection[1] >= self._conf_threshold
        )
        self._streak = self._streak + 1 if is_trigger else 0

        if self._streak >= self._consecutive_frames:
            self._active_until = now + self._jutsu_duration
            self._streak = 0
            return True
        return False

    def force_cast(self):
        """Start a jutsu immediately, bypassing the seal streak. Returns True.

        Used by the manual cast key so the clone effect can be exercised before a seal
        model has been trained.
        """
        self._active_until = self._time_fn() + self._jutsu_duration
        self._streak = 0
        return True

    def is_active(self, now=None):
        if self._active_until is None:
            return False
        now = self._time_fn() if now is None else now
        return now < self._active_until
