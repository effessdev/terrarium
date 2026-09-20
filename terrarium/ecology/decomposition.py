"""Decomposition: rotting matter (detritus) slowly turns into fertile soil.

Damp, warm detritus rots faster.  A rotted cell may also enrich one neighbouring sand
grain, so fertile patches spread around where things died - gardens grow where the
terrarium has been busy.
"""
from __future__ import annotations

import numpy as np

from ..core.system import System
from ..world.materials import DETRITUS, SAND, SOIL

_NEIGH = ((0, 1), (1, 0), (-1, 0), (0, -1))


class DecompositionSystem(System):
    name = "decomposition"
    interval = 10

    def update(self, dt: float) -> None:
        ctx = self.ctx
        g = ctx.grid
        ys, xs = np.nonzero(g.mat == DETRITUS)
        if ys.size == 0:
            return
        half_life = ctx.config.ecology.detritus_half_life
        wet = g.wet[ys, xs].astype(np.float32) / 255.0
        warm = 0.5 + ctx.weather.temperature
        p = (dt / half_life) * 0.693 * (0.25 + 1.5 * wet) * warm
        hit = ctx.rng.np.random(ys.size) < p
        rng = ctx.rng
        for y, x in zip(ys[hit].tolist(), xs[hit].tolist()):
            g.mat[y, x] = SOIL
            g.tint[y, x] = rng.randint(50, 170)
            if rng.chance(0.3):
                dx, dy = rng.choice(_NEIGH)
                if g.mat.item(y + dy, x + dx) == SAND:
                    g.mat[y + dy, x + dx] = SOIL
