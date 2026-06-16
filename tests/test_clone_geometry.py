from jutsu.clone_geometry import clone_paste_rect

# A 100x100 frame with a person 20px wide, 80px tall, horizontally centred.
FRAME_W = 100
FRAME_H = 100
PERSON = (40, 10, 60, 90)


def test_centered_clone_returns_the_full_unclipped_rect():
    rect = clone_paste_rect(FRAME_W, FRAME_H, PERSON, offset_ratio=0.0)

    assert rect == (40, 10, 60, 90, 0, 0, 20, 80)


def test_clone_is_clipped_to_the_right_frame_edge():
    rect = clone_paste_rect(FRAME_W, FRAME_H, PERSON, offset_ratio=2.5)

    assert rect[2] == FRAME_W


def test_clone_entirely_off_the_right_edge_returns_none():
    rect = clone_paste_rect(FRAME_W, FRAME_H, PERSON, offset_ratio=5.0)

    assert rect is None


def test_left_clip_crops_the_source_left_side():
    rect = clone_paste_rect(FRAME_W, FRAME_H, PERSON, offset_ratio=-2.5)

    assert rect[4] == 10


def test_clipped_source_width_matches_destination_width():
    dx1, dy1, dx2, dy2, sx1, sy1, sx2, sy2 = clone_paste_rect(
        FRAME_W, FRAME_H, PERSON, offset_ratio=2.5
    )

    assert (sx2 - sx1) == (dx2 - dx1)
