"""Plant rendering."""

from __future__ import annotations

import pygame

from config import settings
from config.palette import Palette
from entities.plants.plant import Plant


class PlantRenderer:
    """Draws plants."""

    def __init__(
        self,
        palette: Palette,
    ) -> None:
        self.palette = palette

    def render(
        self,
        surface: pygame.Surface,
        plants: list[Plant],
    ) -> None:
        """Render all plants."""
        cell_size = settings.WORLD_CELL_SIZE

        for plant in plants:
            self._render_plant(
                surface,
                plant,
                cell_size,
            )

    def _render_plant(
        self,
        surface: pygame.Surface,
        plant: Plant,
        cell_size: int,
    ) -> None:
        """Render one plant."""
        growth = plant.growth

        if growth <= 0.0:
            return

        base_x = (
            plant.x * cell_size
            + cell_size // 2
        )

        base_y = plant.y * cell_size

        # Mature plants reach roughly 50 pixels.
        height = max(
            2,
            int(52 * growth),
        )

        stem_width = max(
            1,
            int(2 + 2 * growth),
        )

        top_y = base_y - height

        # Stem.
        pygame.draw.rect(
            surface,
            self.palette.plant_dark,
            (
                base_x - stem_width // 2,
                top_y,
                stem_width,
                height,
            ),
        )

        # Leaves become more noticeable as the plant grows.
        if growth > 0.18:
            self._draw_leaf(
                surface,
                base_x - 4,
                top_y + height // 3,
                int(7 * growth),
                True,
            )

        if growth > 0.35:
            self._draw_leaf(
                surface,
                base_x + 5,
                top_y + height // 2,
                int(8 * growth),
                False,
            )

        if growth > 0.55:
            self._draw_leaf(
                surface,
                base_x - 5,
                top_y + int(height * 0.68),
                int(9 * growth),
                True,
            )

        if growth > 0.75:
            self._draw_leaf(
                surface,
                base_x + 5,
                top_y + int(height * 0.82),
                int(8 * growth),
                False,
            )

    def _draw_leaf(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        size: int,
        left: bool,
    ) -> None:
        """Draw a small leaf."""
        size = max(2, size)

        offset = -size if left else size

        pygame.draw.ellipse(
            surface,
            self.palette.plant_light,
            (
                x + offset // 2,
                y - size // 2,
                size,
                max(3, size // 2),
            ),
        )