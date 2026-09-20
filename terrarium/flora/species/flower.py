"""Flower: stem, leaves and a bloom that opens by day and closes at night.

Seeds are only produced after a butterfly / firefly pollinated the flower (with a small
chance of self-seeding, so a world without pollinators is not doomed)."""
from __future__ import annotations

from ...palette.color_utils import jitter
from ...world.materials import SAND, SOIL
from ..base import PlantSpecies
from ..growth import blueprint_step
from ..parts import Part
from ..registry import register

_RING = ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1))


@register
class Flower(PlantSpecies):
    name = "flower"
    substrates = {SOIL: 1.0, SAND: 0.2}
    min_wet = 48
    spacing = 2
    initial_weight = 1.8
    max_population = 70
    growth_rate = 0.7
    lifespan = (380.0, 600.0)
    bite_damage = 0.08
    water_use = 0.009
    light_need = 0.6
    shade_tolerance = 0.3
    seed_interval = (10.0, 20.0)
    seeds_per_event = (2, 4)
    seed_speed = (2.0, 6.0)
    needs_pollination = True
    self_seed_chance = 0.12
    reacts_to_phase = True

    def make_colors(self, palette, rng):
        petal = jitter(rng.choice(palette.petals), rng, dh=4)
        stem = jitter(palette.greens[1], rng, dh=6)
        return {0: stem, int(Part.STEM): stem, int(Part.LEAF): jitter(palette.greens[2], rng, dh=6),
                int(Part.PETAL): petal, int(Part.CENTER): rng.choice(palette.flower_centers)}

    def on_create(self, plant, ctx):
        rng = ctx.rng
        height = rng.randint(7, 13)
        plan = []
        side = rng.sign()
        for h in range(height):
            step = [(0, -h, Part.STEM, h / height)]
            if h >= 2 and h % 2 == 0 and h < height - 2:
                step.append((side, -h, Part.LEAF, 0.6))
                if rng.chance(0.5):
                    step.append((2 * side, -h + 1, Part.LEAF, 0.8))
                side = -side
            plan.append(step)
        plant.data["plan"] = plan
        plant.data["height"] = height
        plant.max_steps = height
        plant.data["head"] = False
        plant.data["open"] = True

    def grow(self, plant, ctx) -> bool:
        return blueprint_step(plant, ctx)

    def on_mature(self, plant, ctx):
        plant.data["head"] = True
        self._set_head(plant, ctx, ctx.clock.is_day)

    def on_phase(self, plant, ctx, is_day):
        if plant.data.get("head") and plant.data["open"] != is_day:
            self._set_head(plant, ctx, is_day)

    def _set_head(self, plant, ctx, open_: bool) -> None:
        cx, cy = plant.x, plant.y - plant.data["height"]
        for dx, dy in _RING:
            plant.remove_cell(ctx, cx + dx, cy + dy)
        plant.add_cell(ctx, cx, cy, Part.CENTER, 0.9)
        cells = _RING if open_ else ((0, -1),)
        for dx, dy in cells:
            plant.add_cell(ctx, cx + dx, cy + dy, Part.PETAL, 0.55 + 0.4 * (dx == 0 or dy == 0))
        plant.data["open"] = open_

    def seed_origin(self, plant):
        return plant.x, plant.y - plant.data["height"] - 2
