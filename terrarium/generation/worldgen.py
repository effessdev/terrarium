"""World generation pipeline.

Each step is an independent function ``step(ctx) -> None`` living in its own module;
``PIPELINE`` lists them in order.  Add, remove or reorder steps here.
"""
from __future__ import annotations

from .moisture import init_moisture
from .ponds import carve_ponds
from .populate import populate
from .rocks import place_rocks
from .terrain import generate_terrain


def _settle(ctx) -> None:
    """Let gravity and water settle the raw shapes before the world starts."""
    gravity = ctx.sim.get("gravity")
    for _ in range(ctx.config.worldgen.settle_ticks):
        gravity.update(ctx.dt)
        ctx.tick += 1


PIPELINE = (generate_terrain, place_rocks, carve_ponds, init_moisture, _settle, populate)


def generate_world(ctx) -> None:
    for step in PIPELINE:
        step(ctx)
    ctx.tick = 0
    ctx.time = 0.0
