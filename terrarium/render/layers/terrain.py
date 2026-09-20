"""Terrain colours (sand, soil, rock, water, detritus, glass) plus tunnels / caves."""
from __future__ import annotations

import numpy as np

from ...world.materials import AIR, GLASS, N_MATERIALS, POROUS, SHADOWS, WATER
from .base import RenderLayer


class TerrainLayer(RenderLayer):
    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        p = ctx.palette
        self.a = np.zeros((N_MATERIALS, 3), np.float32)
        self.b = np.zeros((N_MATERIALS, 3), np.float32)
        pairs = {1: (p.sand_dark, p.sand), 2: (p.soil_dark, p.soil), 3: (p.detritus_dark, p.detritus),
                 4: (p.water_deep, p.water), 5: (p.rock, p.rock_light), 6: (p.glass_edge, p.glass)}
        for m, (lo, hi) in pairs.items():
            self.a[m], self.b[m] = lo, hi
        self.cave = np.array(p.cave, np.float32)
        self.foam = np.array(p.foam, np.float32)
        self.shade_lut = (0.42 + 0.58 * np.exp(-np.arange(256) / 40.0)).astype(np.float32)

    def draw(self, st) -> None:
        g = self.ctx.grid
        mat = g.mat
        t = (g.tint.astype(np.float32) / 255.0)[..., None]
        col = self.a[mat] + (self.b[mat] - self.a[mat]) * t
        wetf = (g.wet.astype(np.float32) / 255.0) * POROUS[mat]
        col *= (1.0 - 0.36 * wetf)[..., None]

        solid = SHADOWS[mat]
        depth = np.cumsum(solid, axis=0, dtype=np.int32)
        above_air = np.empty_like(solid)
        above_air[1:] = mat[:-1] == AIR
        above_air[0] = True
        col[solid & above_air] *= 1.14                         # sunlit top edge

        water = mat == WATER
        if water.any():
            wd = np.cumsum(water, axis=0)
            k = np.clip(wd / 14.0, 0, 1)[..., None]
            wcol = self.b[WATER] + (self.a[WATER] - self.b[WATER]) * k
            shimmer = 1.0 + 0.06 * np.sin(np.arange(g.w)[None, :] * 0.7 + st.time * 2.5)[..., None]
            surf = water & ~np.concatenate([np.zeros((1, g.w), bool), water[:-1]], axis=0)
            wcol = wcol * shimmer
            wcol[surf] = wcol[surf] * 0.6 + self.foam * 0.4
            col = np.where(water[..., None], wcol, col)

        air = mat == AIR
        cave = air & (depth > 0)
        st.sky_mask = air & ~cave & (g.flora == 0)
        solidish = (mat != AIR)
        frame = st.frame
        frame[solidish] = np.minimum(col[solidish], 255).astype(np.uint8)
        cv = np.clip(self.cave * (0.8 + 0.4 * np.exp(-depth[cave][:, None] / 25.0)), 0, 255)
        frame[cave] = cv.astype(np.uint8)
        st.depth = depth
