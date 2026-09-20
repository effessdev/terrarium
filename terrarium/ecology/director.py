"""EcologyDirector: statistics for the HUD and gentle rescue of vanished species.

Rescue = "dormant seeds / eggs in the soil": if a species has been extinct for
``rescue_delay`` simulated seconds, a couple of individuals hatch or germinate at a
suitable place.  This keeps a run interesting without ever touching healthy populations.
Disable it with ``EcologyConfig(rescue_enabled=False)``.
"""
from __future__ import annotations

from collections import defaultdict

from ..core.system import System
from ..fauna.registry import all_species as all_insects
from ..flora.registry import all_species as all_plants
from ..world.materials import WATER


class EcologyDirector(System):
    name = "ecology"
    interval = 30

    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        self._extinct_for: dict[str, float] = defaultdict(float)
        self.rescues = 0

    def update(self, dt: float) -> None:
        ctx = self.ctx
        plants = {s.name: ctx.flora.count(s.name) for s in all_plants()}
        insects = {s.name: ctx.fauna.count(s.name) for s in all_insects()}
        ctx.stats = {
            "plants": plants, "insects": insects,
            "plant_total": sum(plants.values()), "insect_total": sum(insects.values()),
            "seeds": ctx.seeds.count(), "corpses": len(ctx.corpses.corpses),
            "water_cells": int((ctx.grid.mat == WATER).sum()),
            "drips": ctx.water_cycle.drips_total, "rescues": self.rescues,
        }
        if not ctx.config.ecology.rescue_enabled:
            return
        delay = ctx.config.ecology.rescue_delay
        for sp in all_plants():
            if plants[sp.name] == 0:
                self._extinct_for[sp.name] += dt
                if self._extinct_for[sp.name] >= delay and ctx.flora.germinate_random(sp, 2):
                    self._extinct_for[sp.name] = 0.0
                    self.rescues += 1
            else:
                self._extinct_for[sp.name] = 0.0
        for sp in all_insects():
            if insects[sp.name] == 0:
                self._extinct_for[sp.name] += dt
                if self._extinct_for[sp.name] >= delay:
                    made = 0
                    for _ in range(2):
                        spot = ctx.fauna.find_spot(sp)
                        if spot and ctx.fauna.spawn(sp, *spot, juvenile=True):
                            made += 1
                    if made:
                        self._extinct_for[sp.name] = 0.0
                        self.rescues += 1
            else:
                self._extinct_for[sp.name] = 0.0
