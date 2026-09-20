"""SoilMover: insects that dig, carry a grain of sand/soil and drop it elsewhere.

This is what makes the terrain *alive*: ants excavate tunnels below the surface, haul
grains up and build mounds; dry sand around the mounds slumps, wet soil keeps its tunnels.
"""
from __future__ import annotations

from ...world.materials import AIR, COHESION_PY, DIGGABLE_PY, MOVABLE, SHADOWS, SOLID_PY
from .base import Behavior
from .locomotion import DIRS, crawl_step, support_level

_SURFACE = ((0, 1, 3.0), (1, 1, 2.5), (-1, 1, 2.5), (1, 0, 0.8), (-1, 0, 0.8), (1, -1, 0.2), (-1, -1, 0.2))
_TUNNEL = ((0, 1, 1.4), (1, 1, 1.4), (-1, 1, 1.4), (1, 0, 2.6), (-1, 0, 2.6), (1, -1, 0.7), (-1, -1, 0.7), (0, -1, 0.4))


class SoilMover(Behavior):
    def __init__(self, dig_chance: float = 0.10, max_depth: int = 16, carry_limit: int = 50, min_energy: float = 0.3):
        self.dig_chance = dig_chance
        self.max_depth = max_depth
        self.carry_limit = carry_limit
        self.min_energy = min_energy

    def update(self, ins, ctx, dt: float) -> bool:
        if ins.carry is not None:
            return self._carry(ins, ctx)
        if ins.energy < self.min_energy * ins.species.max_energy or ctx.rng.random() > self.dig_chance:
            return False
        return self._dig(ins, ctx)

    # ------------------------------------------------------------------
    def _diggable(self, g, sx, sy, tx, ty) -> bool:
        if not (3 <= tx <= g.w - 4 and 3 <= ty <= g.h - 5):
            return False
        m = g.mat.item(ty, tx)
        if not DIGGABLE_PY[m] or g.wet.item(ty, tx) < 0.5 * COHESION_PY[m]:
            return False
        if ty - g.surface_y(tx) > self.max_depth:
            return False
        ay = ty - 1                                        # the roof must not collapse on us
        if (tx, ay) != (sx, sy):
            am = g.mat.item(ay, tx)
            if MOVABLE[am] and g.wet.item(ay, tx) < COHESION_PY[am]:
                return False
            if g.flora_id.item(ay, tx):                    # do not undermine plants
                return False
        return True

    def _dig(self, ins, ctx) -> bool:
        g = ctx.grid
        x, y = int(ins.x), int(ins.y)
        near_surface = (y - g.surface_y(x)) <= 1
        options = []
        total = 0.0
        for dx, dy, w in (_SURFACE if near_surface else _TUNNEL):
            if self._diggable(g, x, y, x + dx, y + dy):
                options.append((w, x + dx, y + dy))
                total += w
        if not options:
            return False
        r = ctx.rng.random() * total
        chosen = options[-1]
        for opt in options:
            r -= opt[0]
            if r <= 0.0:
                chosen = opt
                break
        _, tx, ty = chosen
        ins.carry = (g.mat.item(ty, tx), g.wet.item(ty, tx), g.tint.item(ty, tx))
        ins.carry_time = 0
        ins.side = ctx.rng.sign()
        g.set_cell(tx, ty, AIR)
        ins.x, ins.y = tx, ty
        ins.energy -= 0.35
        return True

    def _carry(self, ins, ctx) -> bool:
        g = ctx.grid
        rng = ctx.rng
        ins.carry_time += 1
        x, y = int(ins.x), int(ins.y)
        open_sky = not (SHADOWS[g.mat_at(x, y - 1)] or SHADOWS[g.mat_at(x, y - 2)] or SHADOWS[g.mat_at(x, y - 3)])
        if ((open_sky and support_level(g, x, y) >= 2 and rng.random() < 0.35)
                or ins.carry_time > self.carry_limit):
            if self._drop(ins, ctx):
                return True
        if crawl_step(ins, ctx, goal=(x + ins.side * 5, 1), goal_gain=5.0):
            return True
        return self._drop(ins, ctx)

    def _drop(self, ins, ctx) -> bool:
        g = ctx.grid
        x, y = int(ins.x), int(ins.y)
        spots = [(x + dx, y + dy) for dx, dy in DIRS if g.is_air(x + dx, y + dy)]
        if ins.carry_time < 3 * self.carry_limit:          # keep hauling rather than bury a plant
            spots = [(sx, sy) for sx, sy in spots
                     if not g.flora_id[max(0, sy - 1):sy + 2, max(0, sx - 1):sx + 2].any()]
        if not spots:
            return False
        nx, ny = ctx.rng.choice(spots)
        m, wet, tint = ins.carry
        g.set_cell(nx, ny, m, wet, tint)
        ins.carry = None
        return True
