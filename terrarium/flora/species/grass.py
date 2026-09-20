"""Grass: fast, cheap tufts of curved blades.  Regrows when nibbled."""
from __future__ import annotations

from ...palette.color_utils import jitter
from ...world.materials import DETRITUS, SAND, SOIL
from ..base import PlantSpecies
from ..parts import Part
from ..registry import register


@register
class Grass(PlantSpecies):
    name = "grass"
    substrates = {SOIL: 1.0, SAND: 0.22, DETRITUS: 0.6}
    min_wet = 35
    spacing = 1
    initial_weight = 3.0
    max_population = 170
    growth_rate = 1.1
    max_steps = 14
    lifespan = (320.0, 520.0)
    regrows = True
    bite_damage = 0.012
    rot_time = 30.0
    water_use = 0.007
    drought_tolerance = 70.0
    light_need = 0.45
    shade_tolerance = 0.4
    seed_interval = (16.0, 38.0)
    seeds_per_event = (1, 3)
    seed_speed = (2.0, 7.0)

    def make_colors(self, palette, rng):
        base = jitter(palette.greens[rng.randint(1, 3)], rng, dh=6, ds=0.05, dv=0.05)
        return {0: base, int(Part.BLADE): base}

    @staticmethod
    def _cell(plant, blade, i):
        off = int(round(blade["lean"] * i * i / 18.0))
        return plant.x + blade["dx"] + off, plant.y - i

    def on_create(self, plant, ctx):
        plant.data["blades"] = []
        self._new_blade(plant, ctx, first=True)

    def _new_blade(self, plant, ctx, first=False) -> bool:
        rng = ctx.rng
        used = {b["dx"] for b in plant.data["blades"]}
        free = [d for d in (-2, -1, 0, 1, 2) if d not in used]
        if not free:
            return False
        dx = 0 if first else rng.choice(free)
        blade = {"dx": dx, "lean": rng.choice((-1.5, -1, 0, 0, 1, 1.5)), "h": 0, "max": rng.randint(3, 8)}
        x, y = self._cell(plant, blade, 0)
        if plant.add_cell(ctx, x, y, Part.BLADE, 0.0):
            blade["h"] = 1
            plant.data["blades"].append(blade)
            return True
        return False

    def grow(self, plant, ctx) -> bool:
        rng = ctx.rng
        blades = plant.data["blades"]
        growable = [b for b in blades if b["h"] < b["max"]]
        if len(blades) < 5 and (not growable or rng.chance(0.2)):
            if self._new_blade(plant, ctx):
                return True
        if not growable:
            return False
        b = rng.choice(growable)
        x, y = self._cell(plant, b, b["h"])
        if plant.add_cell(ctx, x, y, Part.BLADE, b["h"] / max(1, b["max"] - 1)):
            b["h"] += 1
            return True
        b["max"] = b["h"]
        return False

    def on_eaten(self, plant, ctx, x, y):
        for b in list(plant.data["blades"]):
            for i in range(b["h"]):
                if self._cell(plant, b, i) == (x, y):
                    for j in range(i, b["h"]):
                        plant.remove_cell(ctx, *self._cell(plant, b, j))
                    b["h"] = i
                    if i == 0:
                        plant.data["blades"].remove(b)
                    return
        plant.remove_cell(ctx, x, y)
