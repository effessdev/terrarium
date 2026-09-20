"""Reusable growth helpers shared by several species."""
from __future__ import annotations


def blueprint_step(plant, ctx) -> bool:
    """Pop the next step from ``plant.data['plan']`` and place its cells.

    A plan is a list of steps; each step is a list of ``(dx, dy, part, shade)`` offsets
    relative to the plant anchor.  Returns False once the plan is exhausted."""
    plan = plant.data.get("plan")
    if not plan:
        return False
    for dx, dy, part, shade in plan.pop(0):
        plant.add_cell(ctx, plant.x + dx, plant.y + dy, part, shade)
    return True
