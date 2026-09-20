"""'God tools': paint materials into the world with the mouse (handy for developers too)."""
from __future__ import annotations

from ..world.materials import AIR, GLASS, ROCK, SAND, SOIL, WATER


class Tool:
    name = "tool"
    key = ""

    def apply(self, ctx, x: int, y: int, r: int) -> None:
        g = ctx.grid
        for yy in range(y - r, y + r + 1):
            for xx in range(x - r, x + r + 1):
                if (xx - x) ** 2 + (yy - y) ** 2 <= r * r + 1 and 0 < xx < g.w - 1 and 0 < yy < g.h - 1:
                    self.cell(ctx, xx, yy)

    def cell(self, ctx, x, y) -> None:
        pass


class Paint(Tool):
    def __init__(self, name, key, mat, wet=0) -> None:
        self.name, self.key, self.mat, self.wet = name, key, mat, wet

    def cell(self, ctx, x, y) -> None:
        g = ctx.grid
        if g.mat.item(y, x) == AIR and not g.flora_id.item(y, x) and ctx.rng.random() < 0.6:
            g.set_cell(x, y, self.mat, self.wet, ctx.rng.randint(40, 220))


class Eraser(Tool):
    name, key = "Erase", "5"

    def cell(self, ctx, x, y) -> None:
        g = ctx.grid
        if g.mat.item(y, x) != GLASS:
            g.set_cell(x, y, AIR)
            pid = g.flora_id.item(y, x)
            if pid:
                p = ctx.flora.get(pid)
                if p is not None:
                    p.remove_cell(ctx, x, y)


TOOLS = [Paint("Sand", "1", SAND, 60), Paint("Soil", "2", SOIL, 110), Paint("Water", "3", WATER),
         Paint("Rock", "4", ROCK), Eraser()]
