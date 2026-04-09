from __future__ import annotations

import numpy as np

from M0_Preprocess import fundus_prep


def test_radius_fallback_handles_full_frame_mask() -> None:
    mask = np.ones((860, 1000), dtype=np.uint8)
    center = [429.5, 499.5]

    radius = fundus_prep._get_radius_by_mask_center(mask, center)

    assert radius == 429
