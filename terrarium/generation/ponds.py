"""Step 3: carve basins into the ground and fill them with water."""
from __future__ import annotations

from ..world.materials import AIR, ROCK, SAND, SOIL, WATER


def carve_ponds(ctx) -> None:
    g, rng, p = ctx.grid, ctx.rng, ctx.params
    centres: list[int] = []
    for _ in range(p.n_ponds):
        for _try in range(20):
            cx = rng.randint(18, g.w - 19)
            if all(abs(cx - c) > 40 for c in centres):
                centres.append(cx)
                break
    for cx in centres:
        rw = rng.randint(*p.pond_width)
        depth = rng.randint(4, 9)
        x0, x1 = max(2, cx - rw), min(g.w - 3, cx + rw)
        tops = [g.surface_y(x) for x in range(x0, x1 + 1)]
        level = min(tops[0], tops[-1]) + 1                       # water surface row
        for x in range(x0, x1 + 1):
            t = 1.0 - ((x - cx) / rw) ** 2
            top = g.surface_y(x)
            d = int(depth * t)
            for y in range(top, top + d):
                if g.mat.item(y, x) in (SAND, SOIL):
                    g.mat[y, x] = AIR
            for y in range(level, top + d):
                if g.mat.item(y, x) == AIR:
                    g.set_cell(x, y, WATER)
