"""Mushroom: short-lived decomposer that fruits on rotting matter, mostly at night."""
from __future__ import annotations

from ...palette.color_utils import jitter
from ...world.materials import DETRITUS, SOIL
from ..base import PlantSpecies, clamp
from ..growth import blueprint_step
from ..parts import Part
from ..registry import register


@register
class Mushroom(PlantSpecies):
    name = "mushroom"
    substrates = {DETRITUS: 1.0, SOIL: 0.5}
    min_wet = 80
    spacing = 2
    initial_weight = 0.9
    max_population = 40
    growth_rate = 1.4
    lifespan = (100.0, 180.0)
    rot_time = 25.0
    detritus_yield = 0.8
    water_use = 0.02
    drought_tolerance = 25.0
    light_need = 0.0
    seed_interval = (8.0, 20.0)
    seeds_per_event = (2, 4)
    seed_speed = (3.0, 9.0)

    def make_colors(self, palette, rng):
        cap = jitter(rng.choice(palette.mushroom_caps), rng, dh=5)
        return {0: palette.mushroom_stalk, int(Part.STALK): jitter(palette.mushroom_stalk, rng, dh=4),
                int(Part.CAP): cap}

    def env_factor(self, plant, ctx) -> float:
        night = 1.0 - ctx.clock.daylight
        return clamp(plant.hydration / 0.5) * (0.35 + 0.65 * night)

    def on_create(self, plant, ctx):
        rng = ctx.rng
        stalk = rng.randint(2, 5)
        half = rng.randint(1, 3)
        plan = [[(0, -h, Part.STALK, 0.5)] for h in range(stalk)]
        cap = [(dx, -stalk, Part.CAP, 0.9) for dx in range(-half, half + 1)]
        cap += [(dx, -stalk - 1, Part.CAP, 0.6) for dx in range(-half + 1, half)] or [(0, -stalk - 1, Part.CAP, 0.6)]
        plan.append(cap)
        plant.data["plan"] = plan
        plant.data["top"] = stalk + 1
        plant.max_steps = len(plan)

    def grow(self, plant, ctx) -> bool:
        return blueprint_step(plant, ctx)

    def seed_origin(self, plant):
        return plant.x, plant.y - plant.data["top"] - 1
