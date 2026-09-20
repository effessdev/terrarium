"""Step 2: boulders lying on the ground and stones buried in it."""
from __future__ import annotations

import math

import numpy as np

from ..world.materials import AIR, ROCK, SAND, SOIL


def _blob(g, rng, cx, cy, r, ratio, tint_base) -> None:
    ph1, ph2 = rng.uniform(0, 6.28), rng.uniform(0, 6.28)
    reach = int(r * max(1.0, ratio) * 1.5) + 2
    for y in range(int(cy) - reach, int(cy) + reach + 1):
        for x in range(int(cx) - reach, int(cx) + reach + 1):
            if not (1 < x < g.w - 2 and 1 < y < g.h - 3):
                continue
            dx, dy = (x - cx) / (r * ratio), (y - cy) / r
            ang = math.atan2(dy, dx)
            rr = 1.0 + 0.22 * math.sin(3 * ang + ph1) + 0.12 * math.sin(5 * ang + ph2)
            if dx * dx + dy * dy <= rr * rr:
                m = g.mat.item(y, x)
                if m in (AIR, SAND, SOIL):
                    light = 40 if (dy < -0.2 and dx < 0.3) else 0          # lit upper-left facet
                    g.set_cell(x, y, ROCK, 0, int(min(255, max(0, tint_base + light + rng.randint(-25, 25)))))


def place_rocks(ctx) -> None:
    g, rng, p = ctx.grid, ctx.rng, ctx.params
    surf = p.surface0
    for _ in range(p.n_rocks):
        cx = rng.randint(8, g.w - 9)
        r = rng.uniform(2.5, 8.5)
        cy = int(surf[cx]) - r * rng.uniform(0.0, 0.55)
        _blob(g, rng, cx, cy, r, rng.uniform(0.9, 1.7), rng.randint(90, 150))
    for _ in range(p.n_buried_rocks):
        cx = rng.randint(8, g.w - 9)
        cy = int(surf[cx]) + rng.randint(10, 35)
        _blob(g, rng, cx, min(cy, g.h - 10), rng.uniform(2.5, 6.0), rng.uniform(1.0, 1.8), rng.randint(70, 120))
