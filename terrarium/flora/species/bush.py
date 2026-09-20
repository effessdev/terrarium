"""Bush: a branching woody shrub with leafy tips; the tallest, longest-lived plant."""
from __future__ import annotations

from ...palette.color_utils import jitter
from ...world.materials import SAND, SOIL
from ..base import PlantSpecies
from ..parts import Part
from ..registry import register

_LEAF_OFFSETS = ((-1, 0), (1, 0), (0, -1), (-1, -1), (1, -1), (-1, 1), (1, 1))


@register
class Bush(PlantSpecies):
    name = "bush"
    substrates = {SOIL: 1.0, SAND: 0.15}
    min_wet = 58
    spacing = 5
    initial_weight = 0.7
    max_population = 22
    growth_rate = 0.9
    max_steps = 70
    lifespan = (1500.0, 2600.0)
    rot_time = 90.0
    detritus_yield = 0.55
    bite_damage = 0.004
    water_use = 0.006
    water_capacity = 70.0
    drought_tolerance = 110.0
    root_radius = 5
    root_depth = 7
    light_need = 0.55
    shade_tolerance = 0.35
    seed_interval = (60.0, 120.0)
    seeds_per_event = (1, 2)
    seed_speed = (2.0, 6.0)

    def make_colors(self, palette, rng):
        leaf = jitter(palette.greens[rng.randint(1, 3)], rng, dh=6)
        return {0: palette.wood, int(Part.WOOD): jitter(palette.wood, rng, dh=4),
                int(Part.LEAF): leaf}

    def on_create(self, plant, ctx):
        rng = ctx.rng
        plant.data["limit"] = rng.randint(12, 22)
        plant.data["tips"] = [{"x": 0, "y": 0, "lean": 0}]
        plant.add_cell(ctx, plant.x, plant.y, Part.WOOD, 0.0)

    def grow(self, plant, ctx) -> bool:
        rng = ctx.rng
        tips = plant.data["tips"]
        limit = plant.data["limit"]
        for t in list(tips):
            if -t["y"] >= limit:
                tips.remove(t)
        if not tips:
            return False
        t = rng.choice(tips)
        height = -t["y"]
        if rng.chance(0.35):
            t["lean"] = max(-1, min(1, t["lean"] + rng.choice((-1, 0, 1))))
        dx = t["lean"] if rng.chance(0.55) else 0
        nx, ny = t["x"] + dx, t["y"] - 1
        if not plant.add_cell(ctx, plant.x + nx, plant.y + ny, Part.WOOD, min(1.0, height / limit)):
            tips.remove(t)
            return True
        t["x"], t["y"] = nx, ny
        if height >= 5 and len(tips) < 6 and rng.chance(0.13):
            tips.append({"x": nx, "y": ny, "lean": rng.sign()})
        if height >= 4:
            for _ in range(rng.randint(1, 3)):
                ox, oy = rng.choice(_LEAF_OFFSETS)
                plant.add_cell(ctx, plant.x + nx + ox, plant.y + ny + oy, Part.LEAF, rng.random())
        return True
