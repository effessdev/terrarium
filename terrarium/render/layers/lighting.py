"""Daylight tint and underground darkening (sky cells keep their own gradient)."""
from __future__ import annotations

import numpy as np

from ..common import light_tint
from .base import RenderLayer


class LightingLayer(RenderLayer):
    def draw(self, st) -> None:
        tint = np.array(light_tint(self.ctx), np.float32)
        shade = self.ctx.render_shade_lut[np.minimum(st.depth, 255)]
        mult = (shade * st.mult)[..., None] * tint
        mult[st.sky_mask] = 1.0
        st.frame[:] = np.minimum(st.frame * mult, 255).astype(np.uint8)
