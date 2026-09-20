"""``PlantSpecies``: the data + behaviour description of one kind of plant.

Species objects are stateless singletons.  Per-plant state lives in ``Plant`` (generic)
and ``plant.data`` (species-specific, keep positions *relative to the anchor* so plants
can be shifted when the ground moves).

Minimum a new species has to implement: ``make_colors`` and ``grow`` (and usually
``on_create``).  Everything else has a sensible default.
"""
from __future__ import annotations

import numpy as np

from ..world.materials import DETRITUS, POROUS, SAND, SOIL
from .parts import Part


def clamp(v, lo=0.0, hi=1.0):
    return lo if v < lo else hi if v > hi else v


class PlantSpecies:
    name = "plant"

    # --- placement ---------------------------------------------------------
    substrates = {SOIL: 1.0, SAND: 0.3}   # ground material -> affinity (0 = cannot grow)
    min_wet = 40                           # ground wetness needed to germinate
    spacing = 2                            # free cells required around the anchor
    initial_weight = 1.0                   # relative share of the initial population
    max_population = 120
    rooted = True                          # False: species checks its own support (moss)

    # --- growth --------------------------------------------------------------
    growth_rate = 0.5                      # growth steps per simulated second (ideal conditions)
    max_steps = 12
    lifespan = (400.0, 700.0)
    regrows = False                        # bitten-off parts grow back
    bite_damage = 0.03
    rot_time = 40.0
    detritus_yield = 0.5                   # chance a rotting cell becomes detritus

    # --- needs -----------------------------------------------------------------
    water_use = 0.008                      # hydration fraction consumed per second
    water_capacity = 40.0                  # wetness units stored at full hydration
    drought_tolerance = 60.0               # seconds fully dry before dying
    root_radius = 3
    root_depth = 5
    light_need = 0.5
    shade_tolerance = 0.5
    temp_optimum = 0.6

    # --- reproduction ------------------------------------------------------------
    seed_interval = (30.0, 60.0)
    seeds_per_event = (1, 3)
    seed_speed = (2.0, 6.0)
    needs_pollination = False
    self_seed_chance = 0.0
    reacts_to_phase = False                # receives on_phase() at dawn / dusk

    # ------------------------------------------------------------------ hooks
    def make_colors(self, palette, rng) -> dict:
        raise NotImplementedError

    def on_create(self, plant, ctx) -> None:
        """Place the first cell(s) and initialise ``plant.data``."""

    def grow(self, plant, ctx) -> bool:
        """Add cells for one growth step.  Return False if nothing could be added."""
        raise NotImplementedError

    def on_mature(self, plant, ctx) -> None:
        pass

    def on_eaten(self, plant, ctx, x: int, y: int) -> None:
        plant.remove_cell(ctx, x, y)

    def on_phase(self, plant, ctx, is_day: bool) -> None:
        pass

    def can_seed(self, plant, ctx) -> bool:
        return True

    def seed_origin(self, plant):
        x, y = min(plant.cells, key=lambda c: c[1])
        return x, y - 1

    def support_ok(self, plant, ctx) -> bool:
        """Only used by species with ``rooted = False``."""
        return True

    # ------------------------------------------------------------- environment
    def ground_wetness(self, ctx, x: int, y: int) -> int:
        """Moisture available at the ground below anchor cell (x, y)."""
        g = ctx.grid
        m = g.mat_at(x, y + 1)
        if POROUS[m]:
            return g.wet.item(y + 1, x)
        ratio = float(ctx.vapor.ratio_at(np.array([x]), np.array([y]), ctx.weather.temperature)[0])
        return int(min(255.0, 320.0 * ratio))      # bare rock: only air humidity helps

    def suitability(self, ctx, x: int, y: int) -> float:
        g = ctx.grid
        aff = self.substrates.get(g.mat_at(x, y + 1), 0.0)
        if aff <= 0.0:
            return 0.0
        return aff if self.ground_wetness(ctx, x, y) >= self.min_wet else 0.0

    def env_factor(self, plant, ctx) -> float:
        g = ctx.grid
        light = ctx.weather.light_level
        f_light = 1.0 if self.light_need < 0.05 else clamp(light / self.light_need)
        # neighbours' foliage above us shades us
        x0, x1 = max(0, plant.x - 3), min(g.w, plant.x + 4)
        y0 = max(0, plant.y - 12)
        win = g.flora_id[y0:plant.y, x0:x1]
        others = int(((win != 0) & (win != plant.id)).sum())
        shade = min(1.0, others / 24.0)
        f_light *= 1.0 - shade * (1.0 - self.shade_tolerance)
        f_water = clamp(plant.hydration / 0.5)
        f_temp = clamp(1.25 - abs(ctx.weather.temperature - self.temp_optimum) * 2.0, 0.15, 1.0)
        aff = self.substrates.get(g.mat_at(plant.x, plant.y + 1), 0.4)
        return f_light * f_water * f_temp * (0.35 + 0.65 * aff)

