"""Plants (from the grid layers) and seeds."""
from __future__ import annotations

import numpy as np

from .base import RenderLayer


class FloraLayer(RenderLayer):
    def draw(self, st) -> None:
        g = self.ctx.grid
        m = g.flora > 0
        st.frame[m] = g.flora_rgb[m]
        col = self.ctx.palette.seed
        seeds = self.ctx.seeds
        for s in seeds.airborne:
            x, y = int(s.x), int(s.y)
            if 0 <= x < g.w and 0 <= y < g.h:
                st.frame[y, x] = col
        for s in seeds.landed:
            x, y = int(s.x), int(s.y)
            if 0 <= x < g.w and 0 <= y < g.h:
                st.frame[y, x] = col
