"""Terrain rendering."""

from __future__ import annotations

import pygame

from config import settings
from world.terrain import TerrainType
from world.world import World


class TerrainRenderer:
    """Draws the physical terrain."""

    COLORS = {
        TerrainType.AIR: (27, 34, 31),
        TerrainType.SOIL: (92, 65, 43),
        TerrainType.SAND: (181, 157, 103),
        TerrainType.WATER: (63, 125, 143),
        TerrainType.ROCK: (105, 103, 91),
    }

    def render(
        self,
        surface: pygame.Surface,
        world: World,
    ) -> None:
        """Render every terrain cell."""
        cell_size = settings.WORLD_CELL_SIZE

        for y, row in enumerate(world.terrain):
            for x, cell in enumerate(row):
                color = self.COLORS[
                    cell.terrain_type
                ]

                pygame.draw.rect(
                    surface,
                    color,
                    (
                        x * cell_size,
                        y * cell_size,
                        cell_size,
                        cell_size,
                    ),
                )