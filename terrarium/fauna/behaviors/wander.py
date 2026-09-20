"""Fallback behaviours: aimless walking / flying."""
from __future__ import annotations

from .base import Behavior
from .locomotion import crawl_step, fly_step


class CrawlWander(Behavior):
    def update(self, ins, ctx, dt: float) -> bool:
        rng = ctx.rng
        if rng.chance(0.06):
            ins.dir_idx = rng.randint(0, 7)
        crawl_step(ins, ctx)
        return True


class FlyWander(Behavior):
    def update(self, ins, ctx, dt: float) -> bool:
        fly_step(ins, ctx, dt, ins.species.speed)
        return True
