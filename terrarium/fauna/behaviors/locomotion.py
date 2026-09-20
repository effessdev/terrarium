"""Movement primitives: grid crawling (walls, ceilings, tunnels) and free flying."""
from __future__ import annotations

import math

from ...world.materials import AIR, SOLID_PY, WATER

# 8 neighbours, clockwise starting east (y grows downwards)
DIRS = ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1))
_STEP_W = ((0, 6.0), (1, 2.5), (-1, 2.5), (2, 1.0), (-2, 1.0), (3, 0.3), (-3, 0.3), (4, 0.15))
_SUPPORT_W = (0.0, 0.3, 0.6, 1.0)


def support_level(g, x: int, y: int) -> int:
    """How well a crawler can hold on at (x, y): 3 = ground, 2 = wall / plant, 1 = barely, 0 = none."""
    solid = SOLID_PY
    mat_at = g.mat_at
    if solid[mat_at(x, y + 1)]:
        return 3
    if solid[mat_at(x - 1, y)] or solid[mat_at(x + 1, y)]:
        return 2
    if g.flora.item(y, x):
        return 2
    if (solid[mat_at(x, y - 1)] or solid[mat_at(x - 1, y - 1)] or solid[mat_at(x + 1, y - 1)]
            or solid[mat_at(x - 1, y + 1)] or solid[mat_at(x + 1, y + 1)]):
        return 1
    fl = g.flora
    if (fl.item(y - 1, x) or fl.item(y + 1, x) or fl.item(y, x - 1) or fl.item(y, x + 1)):
        return 1
    return 0


def fall_if_unsupported(ins, ctx) -> bool:
    g = ctx.grid
    x, y = int(ins.x), int(ins.y)
    if support_level(g, x, y) == 0 and g.is_air(x, y + 1):
        ins.x, ins.y = x, y + 1
        return True
    return False


def crawl_step(ins, ctx, goal=None, goal_gain: float = 4.0) -> bool:
    """One weighted random step that keeps holding on to something.

    Prefers continuing straight; with ``goal=(gx, gy)`` steps that reduce the Manhattan
    distance to the goal get a large weight boost."""
    g = ctx.grid
    rng = ctx.rng.py
    x, y = int(ins.x), int(ins.y)
    di = ins.dir_idx
    options = []
    total = 0.0
    for off, wgt in _STEP_W:
        k = (di + off) & 7
        dx, dy = DIRS[k]
        nx, ny = x + dx, y + dy
        if not g.is_air(nx, ny):
            continue
        sup = support_level(g, nx, ny)
        if sup == 0:
            continue
        w = wgt * _SUPPORT_W[sup]
        if goal is not None:
            d0 = abs(goal[0] - x) + abs(goal[1] - y)
            d1 = abs(goal[0] - nx) + abs(goal[1] - ny)
            w *= (1.0 + goal_gain) if d1 < d0 else (0.12 if d1 > d0 else 0.5)
        options.append((w, nx, ny, k))
        total += w
    if not options:
        ins.dir_idx = rng.randrange(8)
        return False
    r = rng.random() * total
    chosen = options[-1]
    for opt in options:
        r -= opt[0]
        if r <= 0.0:
            chosen = opt
            break
    ins.x, ins.y, ins.dir_idx = chosen[1], chosen[2], chosen[3]
    return True


def fly_step(ins, ctx, dt: float, speed: float, goal=None, turn: float = 2.2, clearance: int = 3) -> None:
    """Continuous flight with a wandering heading, optional goal-seeking and wall bounce."""
    g = ctx.grid
    rng = ctx.rng
    h = ins.heading
    if goal is not None:
        desired = math.atan2(goal[1] - ins.y, goal[0] - ins.x)
        diff = (desired - h + math.pi) % (2 * math.pi) - math.pi
        h += diff * min(1.0, 5.0 * dt)
    h += rng.gauss(0.0, turn) * math.sqrt(dt)
    ix = int(ins.x)
    floor_y = g.surface_y(ix) - clearance if goal is None else g.surface_y(ix) - 1
    if ins.y > floor_y:                              # too low: climb
        diff = (-math.pi / 2 - h + math.pi) % (2 * math.pi) - math.pi
        h += diff * min(1.0, 3.0 * dt)
    elif ins.y < 4:                                  # too high: dive
        diff = (math.pi / 2 - h + math.pi) % (2 * math.pi) - math.pi
        h += diff * min(1.0, 3.0 * dt)
    nx = ins.x + math.cos(h) * speed * dt
    ny = ins.y + math.sin(h) * speed * dt
    if g.is_air(int(nx), int(ny)):
        ins.x, ins.y = nx, ny
    else:
        h += math.pi * 0.5 * rng.sign() + rng.gauss(0, 0.4)
    ins.heading = h % (2 * math.pi)


def approach(ins, ctx, dt: float, tx: float, ty: float) -> None:
    if ins.species.locomotion == "crawl":
        crawl_step(ins, ctx, goal=(int(tx), int(ty)), goal_gain=6.0)
    else:
        fly_step(ins, ctx, dt, ins.species.speed, goal=(tx, ty))
