"""Corpses of dead insects: they fall, rot, feed scavengers and finally become detritus."""
from __future__ import annotations

from ..core.system import System
from ..world.materials import AIR, DETRITUS, SOLID_PY, WATER


class Corpse:
    __slots__ = ("x", "y", "color", "age")

    def __init__(self, x: int, y: int, color) -> None:
        self.x, self.y, self.color, self.age = x, y, color, 0.0


class CorpseSystem(System):
    name = "corpses"
    interval = 3
    ROT_TIME = 75.0

    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        self.corpses: list[Corpse] = []

    def add(self, x: int, y: int, color) -> None:
        if len(self.corpses) < 160:
            self.corpses.append(Corpse(x, y, color))

    def remove(self, corpse: Corpse) -> None:
        try:
            self.corpses.remove(corpse)
        except ValueError:
            pass

    def nearest(self, x: int, y: int, radius: int):
        best, bd = None, radius * radius + 1
        for c in self.corpses:
            d = (c.x - x) ** 2 + (c.y - y) ** 2
            if d < bd:
                best, bd = c, d
        return best

    def update(self, dt: float) -> None:
        g = self.ctx.grid
        keep = []
        for c in self.corpses:
            c.age += dt
            m = g.mat_at(c.x, c.y)
            if m != AIR:
                if m == WATER or SOLID_PY[m]:
                    continue                                   # drowned / buried: gone
            if not SOLID_PY[g.mat_at(c.x, c.y + 1)] and g.is_air(c.x, c.y + 1):
                c.y += 1                                        # fall
            if c.age > self.ROT_TIME:
                if g.is_air(c.x, c.y):
                    g.set_cell(c.x, c.y, DETRITUS, wet=110, tint=self.ctx.rng.randint(60, 200))
                continue
            keep.append(c)
        self.corpses = keep
