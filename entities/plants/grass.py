"""Grass plant."""

from __future__ import annotations

from entities.plants.plant import Plant


class Grass(Plant):
    """Simple first plant species."""

    def __init__(
        self,
        x: int,
        y: int,
    ) -> None:
        super().__init__(
            x=x,
            y=y,
            growth_rate=0.10,
        )