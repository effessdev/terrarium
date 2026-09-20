"""Feeding: pluggable *food sources* plus a generic ``Feed`` behaviour.

To let a species eat something new, write a ``FoodSource`` (two methods) and add it to
that species' ``Feed([...])`` list.
"""
from __future__ import annotations

import numpy as np

from ...flora.parts import EDIBLE_LUT, NECTAR_LUT
from ...world.materials import AIR, DETRITUS
from .base import Behavior
from .locomotion import approach


class FoodSource:
    gain = 10.0

    def find(self, ctx, ins, radius: int):
        """Nearest edible thing within ``radius`` as ``(x, y, payload)`` or None."""
        raise NotImplementedError

    def consume(self, ctx, ins, payload) -> float:
        """Eat it; return the energy gained."""
        raise NotImplementedError


class CorpseFood(FoodSource):
    gain = 45.0

    def find(self, ctx, ins, radius):
        c = ctx.corpses.nearest(int(ins.x), int(ins.y), radius)
        return None if c is None else (c.x, c.y, c)

    def consume(self, ctx, ins, payload):
        ctx.corpses.remove(payload)
        return self.gain


class SeedFood(FoodSource):
    gain = 18.0

    def find(self, ctx, ins, radius):
        s = ctx.seeds.nearest_landed(int(ins.x), int(ins.y), radius)
        return None if s is None else (int(s.x), int(s.y), s)

    def consume(self, ctx, ins, payload):
        ctx.seeds.remove(payload)
        return self.gain


class DetritusFood(FoodSource):
    def __init__(self, gain: float = 14.0) -> None:
        self.gain = gain

    def find(self, ctx, ins, radius):
        g = ctx.grid
        x, y = int(ins.x), int(ins.y)
        x0, x1, y0, y1 = max(0, x - radius), min(g.w, x + radius + 1), max(0, y - radius), min(g.h, y + radius + 1)
        ys, xs = np.nonzero(g.mat[y0:y1, x0:x1] == DETRITUS)
        if ys.size == 0:
            return None
        i = int(np.argmin((xs + x0 - x) ** 2 + (ys + y0 - y) ** 2))
        return int(xs[i] + x0), int(ys[i] + y0), None

    def consume(self, ctx, ins, payload):
        g = ctx.grid
        g.set_cell(payload[0], payload[1], AIR)
        return self.gain


class PlantFood(FoodSource):
    """Bites cells off living plants (herbivores)."""

    def __init__(self, gain: float = 9.0, lut=EDIBLE_LUT) -> None:
        self.gain = gain
        self.lut = lut

    def find(self, ctx, ins, radius):
        g = ctx.grid
        x, y = int(ins.x), int(ins.y)
        x0, x1, y0, y1 = max(0, x - radius), min(g.w, x + radius + 1), max(0, y - radius), min(g.h, y + radius + 1)
        ys, xs = np.nonzero(self.lut[g.flora[y0:y1, x0:x1]])
        if ys.size == 0:
            return None
        i = int(np.argmin((xs + x0 - x) ** 2 + (ys + y0 - y) ** 2))
        return int(xs[i] + x0), int(ys[i] + y0), None

    def consume(self, ctx, ins, payload):
        g = ctx.grid
        x, y = payload[0], payload[1]
        plant = ctx.flora.get(g.flora_id.item(y, x))
        if plant is None:
            return 0.0
        plant.eat_cell(ctx, x, y)
        return self.gain


class NectarFood(FoodSource):
    """Sips nectar and pollinates the flower."""
    gain = 24.0

    def find(self, ctx, ins, radius):
        g = ctx.grid
        x, y = int(ins.x), int(ins.y)
        x0, x1, y0, y1 = max(0, x - radius), min(g.w, x + radius + 1), max(0, y - radius), min(g.h, y + radius + 1)
        ys, xs = np.nonzero(NECTAR_LUT[g.flora[y0:y1, x0:x1]])
        if ys.size == 0:
            return None
        order = np.argsort((xs + x0 - x) ** 2 + (ys + y0 - y) ** 2)[:6]
        for i in order:
            px, py = int(xs[i] + x0), int(ys[i] + y0)
            plant = ctx.flora.get(g.flora_id.item(py, px))
            if plant is not None and plant.nectar > 0.3:
                return px, py, None
        return None

    def consume(self, ctx, ins, payload):
        g = ctx.grid
        plant = ctx.flora.get(g.flora_id.item(payload[1], payload[0]))
        if plant is None:
            return 0.0
        plant.nectar -= 0.4
        plant.pollinated = True
        ctx.bus.emit("pollinated", plant=plant)
        return self.gain


class Feed(Behavior):
    """When hungry: eat something in reach, otherwise walk / fly towards the nearest food."""

    def __init__(self, sources, hungry_below: float = 0.7, radius: int = 9, reach: int = 1) -> None:
        self.sources = sources
        self.hungry_below = hungry_below
        self.radius = radius
        self.reach = reach

    def update(self, ins, ctx, dt: float) -> bool:
        sp = ins.species
        if ins.energy > sp.max_energy * self.hungry_below:
            ins.target = None
            return False
        # 1) something within reach?
        for src in self.sources:
            hit = src.find(ctx, ins, self.reach)
            if hit is not None:
                ins.energy = min(sp.max_energy, ins.energy + src.consume(ctx, ins, hit))
                ins.target = None
                return True
        # 2) head for a known / newly found target
        ins.search_cd -= 1
        if ins.target is None and ins.search_cd <= 0:
            ins.search_cd = 5 if sp.locomotion == "crawl" else 15
            best = None
            for src in self.sources:
                hit = src.find(ctx, ins, self.radius)
                if hit is not None:
                    d = (hit[0] - ins.x) ** 2 + (hit[1] - ins.y) ** 2
                    if best is None or d < best[0]:
                        best = (d, hit)
            if best is not None:
                ins.target = (best[1][0], best[1][1])
        if ins.target is not None:
            tx, ty = ins.target
            if abs(tx - ins.x) + abs(ty - ins.y) > self.radius * 2:
                ins.target = None
                return False
            approach(ins, ctx, dt, tx, ty)
            if abs(tx - ins.x) <= self.reach and abs(ty - ins.y) <= self.reach:
                ins.target = None if ctx.rng.chance(0.3) else ins.target
            return True
        return False
