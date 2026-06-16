from jutsu.cast_stabilizer import CastStabilizer


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


def make_stabilizer(consecutive=2, duration=5.0, conf=0.6, clock=None):
    return CastStabilizer(
        trigger_seal="clone",
        conf_threshold=conf,
        consecutive_frames=consecutive,
        jutsu_duration=duration,
        time_fn=clock or FakeClock(),
    )


def test_fires_cast_once_the_streak_is_reached():
    stabilizer = make_stabilizer(consecutive=2)

    stabilizer.update(("clone", 0.9))
    fired = stabilizer.update(("clone", 0.9))

    assert fired is True


def test_does_not_fire_before_the_streak_is_reached():
    stabilizer = make_stabilizer(consecutive=3)

    stabilizer.update(("clone", 0.9))
    fired = stabilizer.update(("clone", 0.9))

    assert fired is False


def test_a_dropped_frame_resets_the_streak():
    stabilizer = make_stabilizer(consecutive=2)

    stabilizer.update(("clone", 0.9))
    stabilizer.update(None)
    fired = stabilizer.update(("clone", 0.9))

    assert fired is False


def test_low_confidence_detection_does_not_count():
    stabilizer = make_stabilizer(consecutive=2, conf=0.6)

    stabilizer.update(("clone", 0.5))
    fired = stabilizer.update(("clone", 0.5))

    assert fired is False


def test_a_different_seal_does_not_count():
    stabilizer = make_stabilizer(consecutive=2)

    stabilizer.update(("tiger", 0.9))
    fired = stabilizer.update(("tiger", 0.9))

    assert fired is False


def test_jutsu_is_active_immediately_after_a_cast():
    stabilizer = make_stabilizer(consecutive=1)

    stabilizer.update(("clone", 0.9))

    assert stabilizer.is_active() is True


def test_jutsu_deactivates_after_its_duration():
    clock = FakeClock()
    stabilizer = make_stabilizer(consecutive=1, duration=5.0, clock=clock)

    stabilizer.update(("clone", 0.9))
    clock.advance(5.1)

    assert stabilizer.is_active() is False


def test_holding_the_seal_does_not_recast_while_active():
    stabilizer = make_stabilizer(consecutive=1, duration=5.0)

    stabilizer.update(("clone", 0.9))
    fired_again = stabilizer.update(("clone", 0.9))

    assert fired_again is False


def test_force_cast_activates_the_jutsu():
    stabilizer = make_stabilizer()

    stabilizer.force_cast()

    assert stabilizer.is_active() is True
