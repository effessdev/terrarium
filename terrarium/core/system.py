"""Base class for everything that advances the simulation.

A *System* owns one concern (gravity, water cycle, plants, insects ...).  Systems are
registered on the :class:`~terrarium.core.simulation.Simulation` in a fixed order and
are called once per ``interval`` ticks with the simulated time step ``dt`` (seconds).

To add a new system:
    1. subclass ``System`` and implement ``update``;
    2. register it in ``terrarium/builder.py``;
    3. optionally expose it on ``SimContext`` if others need to talk to it.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .context import SimContext


class System:
    name: str = "system"
    interval: int = 1          # run every N ticks
    offset: int = 0            # stagger heavy systems so they do not all run on the same tick

    def __init__(self, ctx: "SimContext") -> None:
        self.ctx = ctx

    def update(self, dt: float) -> None:  # pragma: no cover - interface
        raise NotImplementedError
