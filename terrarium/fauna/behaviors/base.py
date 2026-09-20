"""Behaviour interface."""
from __future__ import annotations


class Behavior:
    """One prioritised unit of insect AI.

    ``update`` is called with the insect, the ``SimContext`` and ``dt`` (seconds the
    action represents).  Return True when the behaviour used up the action, which stops
    lower-priority behaviours from running this step.
    """

    def update(self, ins, ctx, dt: float) -> bool:  # pragma: no cover - interface
        return False
