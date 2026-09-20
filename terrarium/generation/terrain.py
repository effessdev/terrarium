"""Step 1: ground shape, sand/soil layers, coloured strata."""
from __future__ import annotations

import numpy as np

from ..world.materials import SAND, SOIL
from .noise import smooth_noise_1d


def generate_terrain(ctx) -> None:
    g, rng, p = ctx.grid, ctx.rng, ctx.params
    npr = rng.np
    w, h = g.w, g.h
    xs = np.arange(w, dtype=np.float32)

    hills = smooth_noise_1d(npr, w, scale=w / 2.5, octaves=3)
    detail = smooth_noise_1d(npr, w, scale=16, octaves=2)
    surface = h * p.ground_level + (hills - 0.5) * h * 0.26 * p.roughness + (detail - 0.5) * 3.0
    for _ in range(p.n_dunes):
        cx, r, a = rng.uniform(w * 0.1, w * 0.9), rng.uniform(14, 34), rng.uniform(3, 10)
        surface -= a * np.exp(-(((xs - cx) / r) ** 2))
    surface = np.clip(surface, h * 0.32, h * 0.86).astype(np.int32)
    ctx.params.surface0 = surface.copy()

    fert = smooth_noise_1d(npr, w, scale=w / 2.2, octaves=2)
    fert = np.clip((fert + (0.5 - p.aridity) * 0.7 - 0.38) * 3.2, 0.0, 1.0)
    thick = fert * rng.uniform(6, 13)

    ys = np.arange(h, dtype=np.int32)[:, None]
    surf = surface[None, :]
    ground = ys >= surf
    is_soil = ground & (ys < surf + thick[None, :])
    g.mat[ground] = SAND
    g.mat[is_soil] = SOIL

    # coloured strata for sand, gradient + speckle for soil
    warp = (hills * 9.0).astype(np.int32)[None, :]
    band = ((ys + warp) // rng.randint(3, 5)) % 4
    band_tint = np.array([70, 150, 215, 105], np.int32)[band]
    noise = npr.normal(0.0, 16.0, (h, w))
    sand_tint = np.clip(band_tint + noise, 0, 255)
    soil_tint = np.clip(190 - (ys - surf) * 9 + npr.normal(0.0, 20.0, (h, w)), 0, 255)
    g.tint[:] = np.where(is_soil, soil_tint, sand_tint).astype(np.uint8)
    g.build_border()
