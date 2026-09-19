"""Terrain rendering."""

from __future__ import annotations

import pygame

from config.palette import Palette
from config import settings
from core.day_night import DayNightCycle
from world.terrain import TerrainType
from world.world import World


def _blend(
    first: tuple[int, int, int],
    second: tuple[int, int, int],
    amount: float,
) -> tuple[int, int, int]:
    """Blend two RGB colors."""
    amount = max(
        0.0,
        min(1.0, amount),
    )

    return tuple(
        int(
            first[index]
            + (
                second[index]
                - first[index]
            )
            * amount
        )
        for index in range(3)
    )


class TerrainRenderer:
    """Draws the physical terrain."""

    def __init__(
        self,
        palette: Palette,
        day_night: DayNightCycle,
    ) -> None:
        self.palette = palette
        self.day_night = day_night

    def render(
        self,
        surface: pygame.Surface,
        world: World,
    ) -> None:
        """Render every terrain cell."""
        cell_size = settings.WORLD_CELL_SIZE

        for y, row in enumerate(world.terrain):
            for x, cell in enumerate(row):
                color = self._get_terrain_color(
                    cell.terrain_type
                )

                color = self._apply_lighting(
                    color
                )

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

        self._draw_sky_indicator(surface)

    def _get_terrain_color(
        self,
        terrain_type: TerrainType,
    ) -> tuple[int, int, int]:
        """Get the palette color for a terrain type."""
        colors = {
            TerrainType.AIR: self.palette.air,
            TerrainType.SOIL: self.palette.soil,
            TerrainType.SAND: self.palette.sand,
            TerrainType.WATER: self.palette.water,
            TerrainType.ROCK: self.palette.rock,
        }

        return colors[terrain_type]

    def _apply_lighting(
        self,
        color: tuple[int, int, int],
    ) -> tuple[int, int, int]:
        """
        Apply inexpensive global day/night lighting.

        This intentionally avoids expensive per-pixel lighting.
        """
        daylight = self.day_night.daylight

        # Night becomes darker, while daytime remains close
        # to the original palette.
        night_amount = 0.42 * (
            1.0 - daylight
        )

        return _blend(
            color,
            self.palette.night_tint,
            night_amount,
        )

    def _draw_sky_indicator(
        self,
        surface: pygame.Surface,
    ) -> None:
        """Draw a small sun/moon indicator."""
        width = settings.WINDOW_WIDTH

        x = int(
            self.day_night.normalized_time
            * (width - 80)
        ) + 40

        # Keep the indicator in the upper part of the sky.
        horizon = (
            settings.WINDOW_HEIGHT * 0.30
        )

        arc_height = 130

        angle = (
            self.day_night.normalized_time
            * math_tau()
        )

        y = int(
            horizon
            - math_sin(angle)
            * arc_height
        )

        y = max(
            35,
            min(
                int(horizon),
                y,
            ),
        )

        color = (
            (244, 205, 105)
            if self.day_night.is_day
            else (190, 200, 220)
        )

        radius = 10

        pygame.draw.circle(
            surface,
            color,
            (x, y),
            radius,
        )


def math_tau() -> float:
    """Small local helper to avoid importing the entire math namespace."""
    import math

    return math.tau


def math_sin(value: float) -> float:
    """Small local helper for the sky arc."""
    import math

    return math.sin(value)