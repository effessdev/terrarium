"""Terrain colours (sand, soil, rock, water, detritus, glass) plus tunnels / caves.

Speed notes: colours come from a (material, tint) -> RGB uint8 lookup table built once;
wetness darkening and the sunlit-edge highlight are written to ``state.mult`` (a float
multiplier per cell) and applied together with the daylight tint in ``LightingLayer``.
"""
from __future__ import annotations

import numpy as np

from ...world.materials import AIR, N_MATERIALS, SHADOWS, WATER
from .base import RenderLayer


class TerrainLayer(RenderLayer):
    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        p = ctx.palette
        pairs = {1: (p.sand_dark, p.sand), 2: (p.soil_dark, p.soil), 3: (p.detritus_dark, p.detritus),
                 4: (p.water_deep, p.water), 5: (p.rock, p.rock_light), 6: (p.glass_edge, p.glass)}
        t = np.linspace(0.0, 1.0, 256, dtype=np.float32)[:, None]
        self.lut = np.zeros((N_MATERIALS, 256, 3), np.uint8)
        for m, (lo, hi) in pairs.items():
            lo, hi = np.array(lo, np.float32), np.array(hi, np.float32)
            self.lut[m] = (lo + (hi - lo) * t).astype(np.uint8)
        self.water_a = np.array(p.water_deep, np.float32)
        self.water_b = np.array(p.water, np.float32)
        self.foam = np.array(p.foam, np.float32)
        self.cave = np.array(p.cave, np.float32)
        self.wet_lut = (1.0 - 0.36 * np.arange(256) / 255.0).astype(np.float32)

    def draw(self, st) -> None:
        g = self.ctx.grid
        mat = g.mat
        frame = st.frame
        solidish = mat != AIR
        frame[solidish] = self.lut[mat, g.tint][solidish]

        st.mult = self.wet_lut[g.wet]                         # (H, W) float32 multiplier
        solid = SHADOWS[mat]
        depth = np.cumsum(solid, axis=0, dtype=np.int16)
        above_air = np.empty_like(solid)
        above_air[1:] = mat[:-1] == AIR
        above_air[0] = True
        st.mult[solid & above_air] *= 1.14                     # sunlit top edge

        water = mat == WATER
        if water.any():
            wd = np.cumsum(water, axis=0, dtype=np.int16)
            ys, xs = np.nonzero(water)
            k = np.clip(wd[ys, xs] / 14.0, 0.0, 1.0)[:, None]
            col = self.water_b + (self.water_a - self.water_b) * k
            col *= (1.0 + 0.06 * np.sin(xs * 0.7 + st.time * 2.5))[:, None]
            top = ~water[ys - 1, xs]
            col[top] = col[top] * 0.6 + self.foam * 0.4
            frame[ys, xs] = np.minimum(col, 255).astype(np.uint8)

        air = ~solidish
        cave = air & (depth > 0)
        st.sky_mask = air & ~cave & (g.flora == 0)
        if cave.any():
            cv = self.cave * (0.8 + 0.4 * np.exp(-depth[cave][:, None] / 25.0))
            frame[cave] = np.minimum(cv, 255).astype(np.uint8)
        st.depth = depth
