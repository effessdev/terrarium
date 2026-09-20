"""Step 4: initial ground moisture - wetter with depth and around ponds."""
from __future__ import annotations

import numpy as np

from ..world.materials import POROUS, WATER
from .noise import box_blur


def init_moisture(ctx) -> None:
    g, p = ctx.grid, ctx.params
    npr = ctx.rng.np
    poro = POROUS[g.mat]
    surf = np.array([g.surface_y(x) for x in range(g.w)])[None, :]
    ys = np.arange(g.h)[:, None]
    depth = np.clip((ys - surf) / np.maximum(g.h - surf, 1), 0.0, 1.0)
    base = (66.0 + 190.0 * depth ** 0.6) * (0.6 + 0.8 * (1.0 - p.aridity))
    halo = box_blur((g.mat == WATER).astype(np.float32), 5) + 0.6 * box_blur((g.mat == WATER).astype(np.float32), 11)
    wet = base + 300.0 * halo + npr.normal(0.0, 6.0, g.mat.shape)
    water = g.mat == WATER
    if water.any():                                   # pond beds sit on a saturated water table
        cols = box_blur(water.any(axis=0).astype(np.float32)[None, :], 4)[0] > 0.02
        top = int(np.nonzero(water.any(axis=1))[0][0])
        wet[(ys >= top) & cols[None, :]] = 255.0
    g.wet[:] = np.where(poro, np.clip(wet, 0, 255), 0).astype(np.uint8)
