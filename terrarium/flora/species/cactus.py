"""Cactus: slow, thick, drought-proof.  Lives on dry sand and blooms once mature."""
from __future__ import annotations

from ...palette.color_utils import jitter
from ...world.materials import SAND, SOIL
from ..base import PlantSpecies
from ..growth import blueprint_step
from ..parts import Part
from ..registry import register


@register
class Cactus(PlantSpecies):
    name = "cactus"
    substrates = {SAND: 1.0, SOIL: 0.3}
    min_wet = 12
    spacing = 4
    initial_weight = 0.8
    max_population = 22
    growth_rate = 0.45
    lifespan = (1600.0, 2800.0)
    rot_time = 80.0
    bite_damage = 0.0
    water_use = 0.0025
    water_capacity = 60.0
    drought_tolerance = 300.0
    root_radius = 4
    root_depth = 4
    light_need = 0.7
    shade_tolerance = 0.15
    temp_optimum = 0.7
    seed_interval = (90.0, 160.0)
    seeds_per_event = (1, 2)
    seed_speed = (1.0, 4.0)

    def make_colors(self, palette, rng):
        body = jitter(palette.cactus, rng, dh=6)
        return {0: body, int(Part.CACTUS): body, int(Part.PETAL): rng.choice(palette.petals)}

    def on_create(self, plant, ctx):
        rng = ctx.rng
        height = rng.randint(6, 12)
        arms = {}
        for _ in range(rng.randint(1, 2)):
            arms[rng.randint(max(2, height // 3), max(3, height - 3))] = (rng.sign(), rng.randint(1, 2), rng.randint(2, 4))
        plan = []
        for h in range(height):
            plan.append([(0, -h, Part.CACTUS, 0.4 + 0.5 * h / height), (1, -h, Part.CACTUS, 0.6 + 0.4 * h / height)])
            if h in arms:
                side, reach, rise = arms[h]
                ax = -reach if side < 0 else 1 + reach
                for k in range(1, reach + 1):
                    plan.append([(-k if side < 0 else 1 + k, -h, Part.CACTUS, 0.5)])
                for j in range(1, rise + 1):
                    plan.append([(ax, -h - j, Part.CACTUS, 0.6 + 0.1 * j)])
        plant.data["plan"] = plan
        plant.data["height"] = height
        plant.max_steps = len(plan)

    def grow(self, plant, ctx) -> bool:
        return blueprint_step(plant, ctx)

    def on_mature(self, plant, ctx):
        h = plant.data["height"]
        plant.add_cell(ctx, plant.x, plant.y - h, Part.PETAL, 0.9)
        plant.add_cell(ctx, plant.x + 1, plant.y - h, Part.PETAL, 0.7)

    def seed_origin(self, plant):
        return plant.x, plant.y - plant.data["height"] - 2
