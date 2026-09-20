"""Rest: flying insects land and sleep when it is not their time of day."""
from __future__ import annotations

from ...world.materials import WATER
from .base import Behavior
from .locomotion import support_level


class Rest(Behavior):
    def __init__(self, threshold: float = 0.2) -> None:
        self.threshold = threshold

    def update(self, ins, ctx, dt: float) -> bool:
        if ins.activity > self.threshold:
            ins.perched = False
            return False
        g = ctx.grid
        x, y = int(ins.x), int(ins.y)
        if support_level(g, x, y) > 0:
            ins.perched = True
            return True
        ny = ins.y + 3.5 * dt
        m = g.mat_at(x, int(ny))
        if g.is_air(x, int(ny)):
            ins.y = ny
        elif m == WATER:
            nx = ins.x + ctx.rng.sign() * 4.0 * dt
            if g.is_air(int(nx), y):
                ins.x = nx
        else:
            ins.perched = True
        return True
