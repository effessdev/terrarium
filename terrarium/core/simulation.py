"""The simulation: an ordered list of systems advanced with a fixed time step."""
from __future__ import annotations

from .context import SimContext
from .system import System


class Simulation:
    def __init__(self, ctx: SimContext) -> None:
        self.ctx = ctx
        self.systems: list[System] = []

    def add(self, system: System) -> System:
        system.offset = len(self.systems) % max(1, system.interval)
        self.systems.append(system)
        return system

    def get(self, name: str) -> System:
        for s in self.systems:
            if s.name == name:
                return s
        raise KeyError(name)

    def tick(self) -> None:
        ctx = self.ctx
        tick_dt = ctx.config.tick_dt
        t = ctx.tick
        for s in self.systems:
            if (t + s.offset) % s.interval == 0:
                s.update(s.interval * tick_dt)
        ctx.tick += 1
        ctx.time += tick_dt
