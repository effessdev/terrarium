"""Moss: a low carpet that creeps over damp soil and rock, even up walls."""
from __future__ import annotations

from ...palette.color_utils import jitter
from ...world.materials import DETRITUS, ROCK, SAND, SOIL, SOLID_PY
from ..base import PlantSpecies
from ..parts import Part
from ..registry import register

_NEIGH = ((1, 0), (-1, 0), (0, -1), (1, -1), (-1, -1), (1, 1), (-1, 1), (0, 1))


@register
class Moss(PlantSpecies):
    name = "moss"
    substrates = {ROCK: 1.0, SOIL: 0.7, DETRITUS: 0.7, SAND: 0.35}
    min_wet = 75
    spacing = 0
    initial_weight = 1.3
    max_population = 45
    rooted = False
    growth_rate = 0.5
    max_steps = 34
    lifespan = (900.0, 1500.0)
    regrows = True
    bite_damage = 0.006
    rot_time = 50.0
    water_use = 0.004
    water_capacity = 30.0
    drought_tolerance = 90.0
    root_radius = 2
    root_depth = 2
    light_need = 0.2
    shade_tolerance = 1.0
    seed_interval = (45.0, 100.0)
    seeds_per_event = (1, 2)
    seed_speed = (1.0, 4.0)

    def make_colors(self, palette, rng):
        c = jitter(palette.greens[rng.randint(1, 3)], rng, dh=8, ds=0.06, dv=0.04)
        return {0: c, int(Part.MOSS): c}

    def on_create(self, plant, ctx):
        plant.add_cell(ctx, plant.x, plant.y, Part.MOSS, ctx.rng.random())

    @staticmethod
    def _supported(g, x, y) -> bool:
        return (SOLID_PY[g.mat_at(x, y + 1)] or SOLID_PY[g.mat_at(x - 1, y)]
                or SOLID_PY[g.mat_at(x + 1, y)] or SOLID_PY[g.mat_at(x, y - 1)])

    def support_ok(self, plant, ctx) -> bool:
        g = ctx.grid
        cells = list(plant.cells)
        for (x, y) in ctx.rng.py.sample(cells, min(5, len(cells))):
            if self._supported(g, x, y):
                return True
        return False

    def grow(self, plant, ctx) -> bool:
        rng = ctx.rng
        g = ctx.grid
        cells = list(plant.cells)
        if not cells:
            return False
        for _ in range(8):
            cx, cy = rng.choice(cells)
            dx, dy = rng.choice(_NEIGH)
            nx, ny = cx + dx, cy + dy
            if g.is_air(nx, ny) and not g.flora_id.item(ny, nx) and self._supported(g, nx, ny):
                if plant.add_cell(ctx, nx, ny, Part.MOSS, rng.random()):
                    return True
        return False
