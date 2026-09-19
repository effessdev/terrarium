"""Grass plant implementation."""

from __future__ import annotations

from entities.plants.plant import Plant


class Grass(Plant):
    """A fast-regrowing grass species used as basic food for worms."""

    def __init__(self, x: int, y: int, growth: float = 0.0) -> None:
        # Higher base growth_rate and modest max_growth to recover
        # quickly from grazing.
        super().__init__(
            x=x,
            y=y,
            growth_rate=0.20,
            max_growth=1.0,
            growth=growth,
        )