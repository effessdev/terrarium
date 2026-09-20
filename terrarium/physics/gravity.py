"""Vectorised falling-sand physics for granular materials and liquids.

Design notes for maintainers
----------------------------
* The whole grid is processed with numpy; there are no per-cell Python loops.
* To avoid two grains claiming the same target cell we process *alternate rows*
  ("parity passes"): sources live on rows of one parity, targets on the other.  Inside a
  pass, straight-down moves never collide; diagonal moves are split into a "left" and a
  "right" sub-pass, each of which also has unique targets.
* A move is a *swap* of all per-cell layers (mat / wet / tint), so grains carry their
  moisture and colour with them and sand sinks through water while water rises.
* Wet grains stick together (``COHESION``): that is what lets soil hold tunnels open and
  lets wet sand keep a steep slope, while dry sand slumps into piles.
"""
from __future__ import annotations

import numpy as np

from ..core.system import System
from ..world.materials import AIR, COHESION, DENSITY, GLASS, MOVABLE, SLIDE, WATER

_DENS_WATER = int(DENSITY[WATER])


def _swap(a_layers, b_layers, mask) -> None:
    if not mask.any():
        return
    for a, b in zip(a_layers, b_layers):
        tmp = a[mask]
        a[mask] = b[mask]
        b[mask] = tmp


class GravitySystem(System):
    name = "gravity"
    interval = 1

    def update(self, dt: float) -> None:
        ctx = self.ctx
        g = ctx.grid
        first = ctx.tick & 1
        for parity in (first, 1 - first):
            self._fall_pass(g, parity)
        for _ in range(ctx.config.physics.lateral_water_passes):
            self._spread_water(g)

    # ------------------------------------------------------------------
    def _fall_pass(self, g, parity: int) -> None:
        rng = self.ctx.rng.np
        rows = np.arange(parity, g.h - 1, 2)
        if rows.size == 0:
            return
        layers = (g.mat, g.wet, g.tint)
        top = [a[rows] for a in layers]
        bot = [a[rows + 1] for a in layers]

        # 1) straight down ---------------------------------------------------
        tm = top[0]
        mobile = MOVABLE[tm] & (top[1] < COHESION[tm])
        _swap(top, bot, mobile & (DENSITY[tm] > DENSITY[bot[0]]))

        # 2) diagonal slides, direction order randomised ----------------------
        for d in ((-1, 1) if self.ctx.rng.py.random() < 0.5 else (1, -1)):
            if d == -1:
                s = [a[:, 1:] for a in top]
                t = [a[:, :-1] for a in bot]
            else:
                s = [a[:, :-1] for a in top]
                t = [a[:, 1:] for a in bot]
            sm = s[0]
            mobile = MOVABLE[sm] & (s[1] < COHESION[sm])
            move = mobile & (DENSITY[sm] > DENSITY[t[0]])
            move &= rng.random(sm.shape, dtype=np.float32) < SLIDE[sm]
            _swap(s, t, move)

        for arr, tb, bb in zip(layers, top, bot):
            arr[rows] = tb
            arr[rows + 1] = bb

    # ------------------------------------------------------------------
    def _spread_water(self, g) -> None:
        m = g.mat
        wrows = np.flatnonzero((m == WATER).any(axis=1))
        if wrows.size == 0:
            return
        y0 = int(wrows[0])
        y1 = min(int(wrows[-1]) + 2, g.h)          # include one row below the lowest water
        rng = self.ctx.rng.np
        order = (-1, 1) if self.ctx.rng.py.random() < 0.5 else (1, -1)
        for d in order:
            sm_all = m[y0:y1]
            below = np.empty_like(sm_all)
            below[:-1] = sm_all[1:]
            below[-1] = GLASS
            rest = (sm_all == WATER) & (DENSITY[below] >= _DENS_WATER)
            rest &= rng.random(sm_all.shape, dtype=np.float32) < 0.6
            layers = [a[y0:y1] for a in (g.mat, g.wet, g.tint)]
            if d == -1:
                src = rest[:, 1:] & (sm_all[:, :-1] == AIR)
                a = [x[:, 1:] for x in layers]
                b = [x[:, :-1] for x in layers]
            else:
                src = rest[:, :-1] & (sm_all[:, 1:] == AIR)
                a = [x[:, :-1] for x in layers]
                b = [x[:, 1:] for x in layers]
            _swap(a, b, src)
