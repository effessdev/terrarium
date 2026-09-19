"""Terrarium world."""

from __future__ import annotations

from utils.randomizer import Randomizer
from world.generation import WorldGenerator
from world.terrain import TerrainCell


class World:
    """Contains the physical state of the terrarium."""

    def __init__(
        self,
        width: int,
        height: int,
        randomizer: Randomizer,
    ) -> None:
        self.width = width
        self.height = height

        self.randomizer = randomizer

        self.generator = WorldGenerator(
            randomizer
        )

        self.terrain: list[list[TerrainCell]] = []

        self.generate()

    def generate(self) -> None:
        """Generate a new world."""
        self.terrain = self.generator.generate(
            self.width,
            self.height,
        )

    def update(self, dt: float) -> None:
        """
        Update world-level simulation.

        Future systems such as water movement and soil
        changes will be connected here.

        For Phase 2, terrain is static.
        """
        _ = dt