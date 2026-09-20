"""Fern: arching fronds with leaflets.  Loves damp, shaded ground."""
from __future__ import annotations

from ...palette.color_utils import jitter
from ...world.materials import DETRITUS, SAND, SOIL
from ..base import PlantSpecies
from ..parts import Part
from ..registry import register


@register
class Fern(PlantSpecies):
    name = "fern"
    substrates = {SOIL: 1.0, DETRITUS: 0.7, SAND: 0.12}
    min_wet = 58
    spacing = 3
    initial_weight = 1.6
    max_population = 60
    growth_rate = 0.75
    max_steps = 26
    lifespan = (520.0, 850.0)
    regrows = True
    bite_damage = 0.02
    water_use = 0.010
    water_capacity = 50.0
    drought_tolerance = 60.0
    light_need = 0.3
    shade_tolerance = 0.9
    seed_interval = (30.0, 60.0)
    seeds_per_event = (1, 3)
    seed_speed = (3.0, 8.0)

    def make_colors(self, palette, rng):
        rib = jitter(palette.greens[0], rng, dh=6)
        leaf = jitter(palette.greens[rng.randint(2, 3)], rng, dh=6)
        return {0: leaf, int(Part.STEM): rib, int(Part.FROND): leaf}

    @staticmethod
    def _cell(plant, f, i):
        d = f["dir"]
        px = plant.x + int(round(d * (i ** 1.25) * 0.22))
        py = plant.y - int(round(i * 0.85 - abs(d) * i * i * 0.02))
        return px, py

    def on_create(self, plant, ctx):
        rng = ctx.rng
        dirs = rng.py.sample([-3, -2, -1, 0, 1, 2, 3], rng.randint(3, 5))
        plant.data["fronds"] = [{"dir": d, "n": 0, "max": rng.randint(6, 11)} for d in dirs]
        plant.add_cell(ctx, plant.x, plant.y, Part.STEM, 0.0)

    def grow(self, plant, ctx) -> bool:
        rng = ctx.rng
        growable = [f for f in plant.data["fronds"] if f["n"] < f["max"]]
        if not growable:
            return False
        f = rng.choice(growable)
        i = f["n"]
        px, py = self._cell(plant, f, i)
        ok = plant.add_cell(ctx, px, py, Part.STEM, 0.3 + 0.5 * i / f["max"])
        if not ok and i > 0:
            f["max"] = f["n"]
            return False
        f["n"] += 1
        if i >= 2 and i % 2 == 1:
            if abs(f["dir"]) <= 1:
                plant.add_cell(ctx, px - 1, py, Part.FROND, 0.8)
                plant.add_cell(ctx, px + 1, py, Part.FROND, 0.8)
            else:
                plant.add_cell(ctx, px, py - 1, Part.FROND, 0.8)
                plant.add_cell(ctx, px, py + 1, Part.FROND, 0.6)
        return True

    def on_eaten(self, plant, ctx, x, y):
        for f in plant.data["fronds"]:
            for i in range(f["n"]):
                if self._cell(plant, f, i) == (x, y) and i > 0:
                    for j in range(i, f["n"]):
                        plant.remove_cell(ctx, *self._cell(plant, f, j))
                    f["n"] = i
                    return
        plant.remove_cell(ctx, x, y)
