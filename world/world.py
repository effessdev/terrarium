"""Terrarium world."""

from __future__ import annotations

from entities.plants.grass import Grass
from entities.plants.plant import Plant
from utils.randomizer import Randomizer
from world.generation import WorldGenerator
from world.terrain import TerrainCell, TerrainType


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

        self.plants: list[Plant] = []

        self.generate()

    def generate(self) -> None:
        """Generate a new world."""
        self.terrain = self.generator.generate(
            self.width,
            self.height,
        )

        self._generate_initial_plants()

    def _generate_initial_plants(self) -> None:
        """Place a small number of initial plants."""
        self.plants.clear()

        attempts = self.randomizer.randint(
            8,
            14,
        )

        for _ in range(attempts):
            x = self.randomizer.randint(
                2,
                self.width - 3,
            )

            surface_y = self._find_surface_y(x)

            if surface_y is None:
                continue

            # Plants grow from the first solid cell.
            plant_y = surface_y

            if self.terrain[plant_y][x].terrain_type not in {
                TerrainType.SOIL,
                TerrainType.SAND,
            }:
                continue

            self.plants.append(
                Grass(
                    x=x,
                    y=plant_y,
                )
            )

    def _find_surface_y(
        self,
        x: int,
    ) -> int | None:
        """Find the uppermost solid terrain cell."""
        for y in range(self.height):
            if self.terrain[y][x].is_solid():
                return y

        return None

    def update(self, dt: float) -> None:
        """Update world-level simulation."""
        _ = dt