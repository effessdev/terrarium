"""Procedural terrarium world generation."""

from __future__ import annotations

import math

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
        """Choose a varied but reasonable average soil level."""
        base_level = int(height * 0.62)

        variation = self.randomizer.randint(
            -5,
            5,
        )

        return max(
            2,
            min(height - 3, base_level + variation),
        )

    def _generate_ground(
        self,
        terrain: list[list[TerrainCell]],
        ground_level: int,
    ) -> None:
        """Generate soil beneath a gently varied natural surface."""
        height = len(terrain)
        width = len(terrain[0])

        surface_points = self._generate_surface(
            width,
            height,
            ground_level,
        )

        for x, surface_y in enumerate(surface_points):
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
        height: int,
        ground_level: int,
    ) -> list[int]:
        """
        Generate a smooth, organic ground surface.

        The surface is built from several low-frequency waves plus a
        small amount of local variation. A short smoothing pass removes
        abrupt cell-to-cell changes while preserving larger hills and
        shallow valleys.
        """
        if width <= 0 or height <= 0:
            return []

        phase_a = self.randomizer.uniform(
            0.0,
            math.tau,
        )
        phase_b = self.randomizer.uniform(
            0.0,
            math.tau,
        )
        phase_c = self.randomizer.uniform(
            0.0,
            math.tau,
        )

        amplitude_a = self.randomizer.uniform(
            2.5,
            5.0,
        )
        amplitude_b = self.randomizer.uniform(
            1.0,
            2.5,
        )
        amplitude_c = self.randomizer.uniform(
            0.4,
            1.2,
        )

        frequency_a = self.randomizer.uniform(
            0.025,
            0.045,
        )
        frequency_b = self.randomizer.uniform(
            0.07,
            0.12,
        )
        frequency_c = self.randomizer.uniform(
            0.14,
            0.22,
        )

        raw_surface: list[float] = []

        for x in range(width):
            broad_shape = (
                math.sin(x * frequency_a + phase_a)
                * amplitude_a
            )

            medium_shape = (
                math.sin(x * frequency_b + phase_b)
                * amplitude_b
            )

            small_shape = (
                math.sin(x * frequency_c + phase_c)
                * amplitude_c
            )

            local_variation = self.randomizer.uniform(
                -0.35,
                0.35,
            )

            raw_surface.append(
                ground_level
                + broad_shape
                + medium_shape
                + small_shape
                + local_variation
            )

        smoothed_surface = raw_surface[:]

        for _ in range(2):
            previous = smoothed_surface[:]

            for x in range(width):
                if x == 0:
                    smoothed_surface[x] = (
                        previous[x] * 0.70
                        + previous[x + 1] * 0.30
                    )
                elif x == width - 1:
                    smoothed_surface[x] = (
                        previous[x - 1] * 0.30
                        + previous[x] * 0.70
                    )
                else:
                    smoothed_surface[x] = (
                        previous[x - 1] * 0.25
                        + previous[x] * 0.50
                        + previous[x + 1] * 0.25
                    )

        minimum_surface = 2
        maximum_surface = max(
            minimum_surface,
            height - 4,
        )

        surface: list[int] = []

        for value in smoothed_surface:
            y = round(value)

            y = max(
                minimum_surface,
                min(maximum_surface, y),
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

        water_count = self.randomizer.randint(
            1,
            2,
        )

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
                        water_depth * edge_factor,
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
        """
        Scatter a small number of large, irregular rock formations.

        Rocks are intentionally much larger than the original one- or
        two-cell rocks, so the number of formations is kept low.
        """
        width = len(terrain[0])
        height = len(terrain)

        rock_count = self.randomizer.randint(
            4,
            8,
        )

        for _ in range(rock_count):
            x = self.randomizer.randint(
                3,
                width - 4,
            )

            surface_y = self._find_surface_y(
                terrain,
                x,
                ground_level,
            )

            rock_width = self.randomizer.randint(
                3,
                6,
            )

            rock_height = self.randomizer.randint(
                2,
                4,
            )

            half_width = rock_width // 2

            # Give each rock a slightly different profile.
            column_heights: list[int] = []

            for offset in range(rock_width):
                distance = abs(offset - half_width)
                edge_factor = 1.0 - (
                    distance / max(1, half_width + 1)
                )

                variation = self.randomizer.uniform(
                    -0.6,
                    0.6,
                )

                column_height = max(
                    1,
                    round(
                        rock_height
                        * (0.65 + edge_factor * 0.35)
                        + variation,
                    ),
                )

                column_heights.append(column_height)

            for offset, column_height in enumerate(
                column_heights
            ):
                rock_x = (
                    x
                    - half_width
                    + offset
                )

                if not 0 <= rock_x < width:
                    continue

                column_surface_y = self._find_surface_y(
                    terrain,
                    rock_x,
                    ground_level,
                )

                # Keep the formation attached to the local terrain
                # rather than forcing every column to one height.
                top_y = column_surface_y - (
                    column_height - 1
                )

                for y in range(
                    top_y,
                    column_surface_y + 1,
                ):
                    if 0 <= y < height:
                        terrain[y][rock_x] = TerrainCell(
                            terrain_type=TerrainType.ROCK,
                            moisture=0.05,
                            nutrients=0.0,
                        )