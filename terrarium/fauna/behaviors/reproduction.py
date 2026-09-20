"""Reproduction: find a mate of the same species, meet, pay energy, give birth."""
from __future__ import annotations

from .base import Behavior
from .locomotion import approach


class Reproduce(Behavior):
    def __init__(self, mate_radius: int = 9) -> None:
        self.mate_radius = mate_radius

    def update(self, ins, ctx, dt: float) -> bool:
        if not ins.can_breed():
            return False
        sp = ins.species
        fauna = ctx.fauna
        mate = fauna.find_mate(ins, self.mate_radius)
        if mate is None:
            return False
        dist = max(abs(mate.x - ins.x), abs(mate.y - ins.y))
        if dist > 2.0:
            approach(ins, ctx, dt, mate.x, mate.y)
            return True
        pop, cap = fauna.count(sp.name), sp.max_population
        rng = ctx.rng
        for who in (ins, mate):
            who.cooldown = sp.repro_cooldown * rng.uniform(0.8, 1.3)
        if pop >= cap or rng.random() > 1.0 - pop / cap:    # crowding suppresses births
            return True
        for who in (ins, mate):
            who.energy -= sp.repro_cost * 0.5
        for _ in range(rng.randint(*sp.litter)):
            fauna.spawn(sp, int(ins.x), int(ins.y), juvenile=True)
        return True
