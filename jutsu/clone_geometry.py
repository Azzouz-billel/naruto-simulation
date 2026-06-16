"""Pure geometry for placing a person cutout as an offset clone.

Kept free of OpenCV/numpy so the clipping math can be unit-tested directly.
"""


def clone_paste_rect(frame_w, frame_h, person_bbox, offset_ratio):
    """Map a person cutout shifted horizontally to a clipped paste rectangle.

    The cutout occupies `person_bbox` `(x1, y1, x2, y2)` in the original frame. A clone is
    that cutout translated by `offset_ratio * person_width` along x. Returns
    `(dst_x1, dst_y1, dst_x2, dst_y2, src_x1, src_y1, src_x2, src_y2)` where the `dst` rect
    is clipped to the frame and the `src` rect is the matching crop in cutout-local
    coordinates (origin at the bbox top-left). Returns `None` if the clone falls entirely
    off-screen.
    """
    x1, y1, x2, y2 = person_bbox
    person_w = x2 - x1
    dx = int(round(offset_ratio * person_w))

    dst_x1, dst_y1, dst_x2, dst_y2 = x1 + dx, y1, x2 + dx, y2

    clipped_x1 = max(0, dst_x1)
    clipped_y1 = max(0, dst_y1)
    clipped_x2 = min(frame_w, dst_x2)
    clipped_y2 = min(frame_h, dst_y2)
    if clipped_x1 >= clipped_x2 or clipped_y1 >= clipped_y2:
        return None

    src_x1 = clipped_x1 - dst_x1
    src_y1 = clipped_y1 - dst_y1
    src_x2 = src_x1 + (clipped_x2 - clipped_x1)
    src_y2 = src_y1 + (clipped_y2 - clipped_y1)

    return (clipped_x1, clipped_y1, clipped_x2, clipped_y2, src_x1, src_y1, src_x2, src_y2)
