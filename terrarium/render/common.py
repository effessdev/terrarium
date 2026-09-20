"""Shared render helpers and the per-frame ``RenderState``."""
from __future__ import annotations

import numpy as np


class RenderState:
    """Scratch data shared by the layers of one frame."""
    def __init__(self, w: int, h: int) -> None:
        self.frame = np.zeros((h, w, 3), np.uint8)
        self.sky_mask = np.zeros((h, w), bool)
        self.time = 0.0


def blend3(day_w, night_w, twi_w, day, night, twi):
    return tuple(day_w * day[i] + night_w * night[i] + twi_w * twi[i] for i in range(len(day)))


def light_tint(ctx):
    """Current (r, g, b) light multiplier from the palette keyframes."""
    pal, clock = ctx.palette, ctx.clock
    d, n, t, morning = clock.phase_weights()
    twi = pal.light_dawn if morning else pal.light_dusk
    dim = 0.75 + 0.25 * ctx.weather.sunniness
    day = tuple(c * (dim if i < 3 else 1) for i, c in enumerate(pal.light_day))
    return blend3(d, n, t, day, pal.light_night, twi)
