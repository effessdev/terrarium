"""Ground hydrology: soaking, draining and capillary spreading of moisture.

Water *cells* soak into porous ground (sand, soil, detritus) and become wetness (0-255)
stored in ``grid.wet``.  Wetness above a material's field capacity drains downwards;
below it, wetness slowly equalises with porous neighbours (capillarity).  Evaporation
and plant uptake remove wetness elsewhere (see ``climate/water_cycle.py`` and
``flora/plant.py``).
"""
from __future__ import annotations

import numpy as np

from ..core.system import System
from ..world.materials import AIR, FIELD_CAP, POROUS, WATER


class MoistureSystem(System):
    name = "moisture"

    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        self.interval = ctx.config.physics.moisture_interval

    def update(self, dt: float) -> None:
        g = self.ctx.grid
        cfg = self.ctx.config.physics
        self._absorb(g, cfg)
        self._spread(g, cfg)

    # ------------------------------------------------------------------
    def _absorb(self, g, cfg) -> None:
        m, wet = g.mat, g.wet
        ys, xs = np.nonzero(m == WATER)
        if ys.size == 0:
            return
        rng = self.ctx.rng.np
        porous = POROUS[m]
        h, w = g.h, g.w
        gain = cfg.water_to_wet
        # candidate targets: below, left, right of every water cell
        for dy, dx in ((1, 0), (0, -1), (0, 1)):
            ty, tx = ys + dy, xs + dx
            ok = (ty < h) & (tx >= 0) & (tx < w)
            ty, tx, sy, sx = ty[ok], tx[ok], ys[ok], xs[ok]
            ok = porous[ty, tx] & (wet[ty, tx] < 170) & (m[sy, sx] == WATER)
            ok &= rng.random(ok.shape) < cfg.absorb_chance
            if not ok.any():
                continue
            ty, tx, sy, sx = ty[ok], tx[ok], sy[ok], sx[ok]
            m[sy, sx] = AIR
            wet[ty, tx] = np.minimum(255, wet[ty, tx].astype(np.int16) + gain).astype(np.uint8)

    # ------------------------------------------------------------------
    def _spread(self, g, cfg) -> None:
        m = g.mat
        porous = POROUS[m]
        if not porous.any():
            return
        w = g.wet.astype(np.float32)
        w *= porous
        # gravity drain of the excess over field capacity
        cap = FIELD_CAP[m]
        excess = np.maximum(w - cap, 0.0)
        room = (255.0 - w[1:]) * porous[1:]
        flow = np.minimum(excess[:-1], room) * porous[:-1] * cfg.drain_rate
        w[:-1] -= flow
        w[1:] += flow
        # capillary diffusion among porous neighbours
        p = porous.astype(np.float32)
        wp = w * p
        num = np.zeros_like(w)
        cnt = np.zeros_like(w)
        num[1:] += wp[:-1]; cnt[1:] += p[:-1]
        num[:-1] += wp[1:]; cnt[:-1] += p[1:]
        num[:, 1:] += wp[:, :-1]; cnt[:, 1:] += p[:, :-1]
        num[:, :-1] += wp[:, 1:]; cnt[:, :-1] += p[:, 1:]
        avg = num / np.maximum(cnt, 1.0)
        w = np.where(porous & (cnt > 0), w + cfg.diffusion_rate * (avg - w), w)
        g.wet[:] = np.where(porous, np.clip(np.rint(w), 0, 255), 0).astype(np.uint8)
