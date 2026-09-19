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
        variation = plant.variation
        sway = int((variation - 0.5) * 10)
        leaf_scale = 0.8 + variation * 0.9

        # Mature plants reach roughly 50 pixels.
        height = max(
            2,
            int(52 * growth),
        )

        stem_width = max(
            1,
            int((2 + 2 * growth) + variation * 2.0),
        )

        top_y = base_y - height
        stem_center_x = base_x + sway

        # Tapering stem gives each plant a more natural silhouette.
        stem_points = [
            (stem_center_x - stem_width // 2, top_y + height * 0.16),
            (stem_center_x + stem_width // 2, top_y),
            (stem_center_x + stem_width // 2 + sway // 2, base_y),
            (stem_center_x - stem_width // 2 - sway // 2, base_y - height * 0.12),
        ]
        pygame.draw.polygon(
            surface,
            self.palette.plant_dark,
            stem_points,
        )

        # Leaves become more noticeable as the plant grows.
        if growth > 0.18:
            self._draw_leaf(
                surface,
                base_x - 4 + sway,
                top_y + height // 3,
                max(2, int((7 * growth) * leaf_scale)),
                True,
            )

        if growth > 0.35:
            self._draw_leaf(
                surface,
                base_x + 5 + sway,
                top_y + height // 2,
                max(2, int((8 * growth) * leaf_scale)),
                False,
            )

        if growth > 0.55:
            self._draw_leaf(
                surface,
                base_x - 5 + sway,
                top_y + int(height * 0.68),
                max(2, int((9 * growth) * leaf_scale)),
                True,
            )

        if growth > 0.75:
            self._draw_leaf(
                surface,
                base_x + 5 + sway,
                top_y + int(height * 0.82),
                max(2, int((8 * growth) * leaf_scale)),
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
        """Draw a small organic leaf."""
        size = max(2, size)
        direction = -1 if left else 1

        points = [
            (x, y - size // 2),
            (x + direction * int(size * 0.8), y - size // 3),
            (x + direction * size, y),
            (x + direction * int(size * 0.8), y + size // 3),
            (x, y + size // 2),
            (x - direction * int(size * 0.5), y),
        ]

        pygame.draw.polygon(
            surface,
            self.palette.plant_light,
            points,
        )