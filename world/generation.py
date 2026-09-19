"""Procedural terrarium world generation."""

from __future__ import annotations

import math

from config import settings
from utils.randomizer import Randomizer
from world.terrain import TerrainCell, TerrainType


class WorldGenerator:
    """Creates the initial terrain layout."""

    def __init__(self, randomizer: Randomizer) -> None:
        self.randomizer = randomizer

    def generate(
        self,
        width: int,
        height: int,
    ) -> list[list[TerrainCell]]:
        """Generate a complete terrain grid."""
        terrain = self._create_empty_grid(width, height)

        ground_level = self._choose_ground_level(height)

        self._generate_ground(
            terrain,
            ground_level,
        )

        self._generate_water(
            terrain,
            ground_level,
        )

        self._generate_rocks(
            terrain,
            ground_level,
        )

        return terrain

    def _create_empty_grid(
        self,
        width: int,
        height: int,
    ) -> list[list[TerrainCell]]:
        """Create an empty air-filled grid."""
        return [
            [
                TerrainCell()
                for _ in range(width)
            ]
            for _ in range(height)
        ]

    def _choose_ground_level(self, height: int) -> int:
        """Choose a varied but reasonable soil level."""
        base_level = int(height * 0.62)

        variation = self.randomizer.randint(
            -5,
            5,
        )

        return base_level + variation

    def _generate_ground(
        self,
        terrain: list[list[TerrainCell]],
        ground_level: int,
    ) -> None:
        """Generate soil with a naturally uneven surface."""
        height = len(terrain)
        width = len(terrain[0])

        surface_points = self._generate_surface(
            width,
            ground_level,
        )

        for x in range(width):
            surface_y = surface_points[x]

            for y in range(surface_y, height):
                depth = y - surface_y

                if depth <= 2:
                    terrain[y][x] = TerrainCell(
                        terrain_type=TerrainType.SAND,
                        moisture=0.15,
                        nutrients=0.35,
                    )
                else:
                    terrain[y][x] = TerrainCell(
                        terrain_type=TerrainType.SOIL,
                        moisture=0.30,
                        nutrients=0.65,
                    )

    def _generate_surface(
        self,
        width: int,
        ground_level: int,
    ) -> list[int]:
        """
        Generate a gently varying ground surface.

        Multiple low-frequency waves make the terrain look organic
        without requiring a full noise library.
        """
        phase_a = self.randomizer.uniform(
            0.0,
            math.tau,
        )

        phase_b = self.randomizer.uniform(
            0.0,
            math.tau,
        )

        amplitude_a = self.randomizer.uniform(
            2.0,
            4.0,
        )

        amplitude_b = self.randomizer.uniform(
            1.0,
            2.5,
        )

        frequency_a = self.randomizer.uniform(
            0.035,
            0.055,
        )

        frequency_b = self.randomizer.uniform(
            0.08,
            0.13,
        )

        surface = []

        for x in range(width):
            wave_a = math.sin(
                x * frequency_a + phase_a
            ) * amplitude_a

            wave_b = math.sin(
                x * frequency_b + phase_b
            ) * amplitude_b

            small_random = self.randomizer.uniform(
                -0.4,
                0.4,
            )

            y = round(
                ground_level
                + wave_a
                + wave_b
                + small_random
            )

            y = max(
                1,
                min(len(surface) + 0, y),
            )

            surface.append(y)

        return surface

    def _generate_water(
        self,
        terrain: list[list[TerrainCell]],
        ground_level: int,
    ) -> None:
        """Create one or two shallow water regions."""
        width = len(terrain[0])
        height = len(terrain)

        water_count = self.randomizer.randint(1, 2)

        for _ in range(water_count):
            center_x = self.randomizer.randint(
                width // 6,
                width - width // 6,
            )

            radius = self.randomizer.randint(
                7,
                16,
            )

            water_depth = self.randomizer.randint(
                1,
                3,
            )

            for x in range(
                max(0, center_x - radius),
                min(width, center_x + radius + 1),
            ):
                distance = abs(x - center_x)

                if distance > radius:
                    continue

                edge_factor = 1.0 - (
                    distance / radius
                )

                local_depth = max(
                    1,
                    round(
                        water_depth
                        * edge_factor
                    ),
                )

                surface_y = self._find_surface_y(
                    terrain,
                    x,
                    ground_level,
                )

                for depth in range(local_depth):
                    y = surface_y - depth

                    if 0 <= y < height:
                        terrain[y][x] = TerrainCell(
                            terrain_type=TerrainType.WATER,
                            moisture=1.0,
                            nutrients=0.1,
                        )

    def _find_surface_y(
        self,
        terrain: list[list[TerrainCell]],
        x: int,
        fallback: int,
    ) -> int:
        """Find the uppermost solid cell at a column."""
        height = len(terrain)

        for y in range(height):
            if terrain[y][x].is_solid():
                return y

        return fallback

    def _generate_rocks(
        self,
        terrain: list[list[TerrainCell]],
        ground_level: int,
    ) -> None:
        """Scatter a small number of rocks across the terrain."""
        width = len(terrain[0])
        height = len(terrain)

        rock_count = self.randomizer.randint(
            12,
            24,
        )

        for _ in range(rock_count):
            x = self.randomizer.randint(
                2,
                width - 3,
            )

            surface_y = self._find_surface_y(
                terrain,
                x,
                ground_level,
            )

            # Some rocks remain partly buried.
            y = surface_y - self.randomizer.randint(
                0,
                1,
            )

            if 0 <= y < height:
                terrain[y][x] = TerrainCell(
                    terrain_type=TerrainType.ROCK,
                    moisture=0.05,
                    nutrients=0.0,
                )

                # Occasionally create a second cell,
                # giving the rock a slightly larger shape.
                if (
                    self.randomizer.chance(0.35)
                    and x + 1 < width
                ):
                    terrain[y][x + 1] = TerrainCell(
                        terrain_type=TerrainType.ROCK,
                        moisture=0.05,
                        nutrients=0.0,
                    )
