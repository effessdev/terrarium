"""The water cycle: evaporation -> vapour -> condensation on the lid -> drips (rain).

* Exposed water cells and damp exposed ground evaporate (more when warm and sunny, less
  when the surrounding air is already humid).
* Vapour spreads and rises in a coarse field (``VaporField``); plants add to it by
  transpiration (``flora/plant.py``).
* Where the air is over-saturated near the glass lid, droplets accumulate on the lid
  (``lid_drops``); when a droplet grows big enough it falls as a real water cell.
"""
from __future__ import annotations

import numpy as np

from ..core.system import System
from ..world.materials import AIR, POROUS, WATER
from .vapor import VaporField


class WaterCycleSystem(System):
    name = "water_cycle"

    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        cc = ctx.config.climate
        self.interval = cc.evap_interval
        g = ctx.grid
        self.vapor = VaporField(g.w, g.h, cc.vapor_capacity, cc.vapor_diffusion, cc.vapor_rise)
        ctx.vapor = self.vapor
        self.lid_drops = np.zeros(g.w, np.float32)     # droplet size per column, 0..threshold
        self.drips_total = 0
        self.evaporated_total = 0.0

    def update(self, dt: float) -> None:
        ctx = self.ctx
        g = ctx.grid
        cc = ctx.config.climate
        temp = ctx.weather.temperature
        heat = 0.15 + 1.6 * temp * (0.4 + 0.6 * ctx.weather.sunniness) * (0.35 + 0.65 * ctx.clock.daylight)
        self._evaporate(g, cc, temp, heat)
        condensed = self.vapor.step(temp, cc.condensation_rate)
        self._deposit_on_lid(g, condensed)
        self._drip(g, cc)

    # ------------------------------------------------------------------
    def _evaporate(self, g, cc, temp, heat) -> None:
        rng = self.ctx.rng.np
        m = g.mat
        above = np.empty_like(m)
        above[1:] = m[:-1]
        above[0] = AIR
        exposed = above == AIR
        # open water
        ys, xs = np.nonzero((m == WATER) & exposed)
        if ys.size:
            hum = np.clip(self.vapor.ratio_at(xs, ys, temp), 0.0, 1.0)
            p = cc.evaporation_water * heat * (1.0 - hum)
            hit = rng.random(ys.size) < p
            if hit.any():
                hy, hx = ys[hit], xs[hit]
                m[hy, hx] = AIR
                self.vapor.add_many(hx, hy, np.ones(hy.size, np.float32))
                self.evaporated_total += float(hy.size)
        # damp ground surface
        wet = g.wet
        ys, xs = np.nonzero(POROUS[m] & exposed & (wet > 25))
        if ys.size:
            hum = np.clip(self.vapor.ratio_at(xs, ys, temp), 0.0, 1.0)
            frac = wet[ys, xs].astype(np.float32) / 255.0
            lost = np.minimum(wet[ys, xs].astype(np.float32),
                              cc.evaporation_soil * heat * (1.0 - hum) * (0.3 + frac))
            lost = np.floor(lost + rng.random(ys.size)).astype(np.int16)
            wet[ys, xs] = np.maximum(wet[ys, xs].astype(np.int16) - lost, 0).astype(np.uint8)
            self.vapor.add_many(xs, ys, lost.astype(np.float32) / self.ctx.config.physics.water_to_wet)

    def _deposit_on_lid(self, g, condensed) -> None:
        if condensed.max() <= 0.0:
            return
        rng = self.ctx.rng.np
        b = VaporField.BLOCK
        cols = np.nonzero(condensed > 0)[0]
        off = rng.integers(0, b, cols.size)
        idx = np.minimum(cols * b + off, g.w - 2)
        np.add.at(self.lid_drops, idx, condensed[cols])

    def _drip(self, g, cc) -> None:
        ripe = np.nonzero(self.lid_drops >= cc.drip_threshold)[0]
        for x in ripe:
            x = int(x)
            if g.mat.item(1, x) == AIR:
                g.set_cell(x, 1, WATER)
                self.lid_drops[x] -= cc.drip_threshold
                self.drips_total += 1
            else:
                self.lid_drops[x] = cc.drip_threshold * 0.9   # wait for room
