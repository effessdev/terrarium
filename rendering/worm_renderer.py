"""Worm rendering."""

from __future__ import annotations

import math

import pygame

from config import settings
from config.palette import Palette
from entities.worms.worm import Worm, WormState


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
            ) * amount
        )
        for index in range(3)
    )


class WormRenderer:
    """Draws living worms and decomposing worm corpses."""

    def __init__(
        self,
        palette: Palette,
        font: pygame.font.Font,
    ) -> None:
        self.palette = palette
        self.font = font

    def render(
        self,
        surface: pygame.Surface,
        worms: list[Worm],
    ) -> None:
        """Render all worms."""
        cell_size = settings.WORLD_CELL_SIZE

        for worm in worms:
            self._render_worm(
                surface,
                worm,
                cell_size,
            )

    def _render_worm(
        self,
        surface: pygame.Surface,
        worm: Worm,
        cell_size: int,
    ) -> None:
        """Render one worm."""
        x = int(
            worm.x * cell_size
            + cell_size // 2
        )

        y = int(
            worm.y * cell_size
            + cell_size // 2
        )

        if worm.is_dead:
            self._render_corpse(
                surface,
                worm,
                x,
                y,
            )
            return

        if worm.state == WormState.SLEEPING:
            self._render_sleeping(
                surface,
                worm,
                x,
                y,
            )
            return

        self._render_living(
            surface,
            worm,
            x,
            y,
        )

    def _render_living(
        self,
        surface: pygame.Surface,
        worm: Worm,
        x: int,
        y: int,
    ) -> None:
        """Render a living worm according to its condition."""
        base_color = self.palette.insect

        if worm.thirst >= settings.WORM_THIRST_THRESHOLD:
            color = _blend(
                base_color,
                (180, 195, 215),
                min(
                    1.0,
                    worm.thirst,
                ) * 0.45,
            )
        elif worm.hunger >= settings.WORM_HUNGER_THRESHOLD:
            color = _blend(
                base_color,
                (125, 82, 55),
                min(
                    1.0,
                    worm.hunger,
                ) * 0.40,
            )
        else:
            color = base_color

        size = max(
            3,
            int(
                3.0
                + worm.size * 4.0
            ),
        )

        if worm.state == WormState.SLEEPING:
            self._draw_sleeping_body(
                surface,
                x,
                y,
                size,
                color,
            )
            return

        self._draw_worm_body(
            surface,
            worm,
            x,
            y,
            size,
            color,
        )

    def _draw_worm_body(
        self,
        surface: pygame.Surface,
        worm: Worm,
        x: int,
        y: int,
        size: int,
        color: tuple[int, int, int],
    ) -> None:
        """Draw an extended worm."""
        direction = worm.direction

        segments = max(
            3,
            int(
                4
                + worm.growth * 4
            ),
        )

        length = size * 2

        for index in range(segments):
            progress = (
                index / max(
                    1,
                    segments - 1,
                )
            )

            segment_x = int(
                x
                - direction
                * progress
                * length
            )

            wave = math.sin(
                progress * math.pi * 2.0
            )

            segment_y = int(
                y
                + wave * 2.0
            )

            radius = max(
                2,
                int(
                    size
                    * (
                        0.75
                        - progress * 0.15
                    )
                ),
            )

            pygame.draw.circle(
                surface,
                color,
                (segment_x, segment_y),
                radius,
            )

    def _draw_sleeping_body(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        size: int,
        color: tuple[int, int, int],
    ) -> None:
        """Draw a worm curled into a sleeping circle."""
        outer_radius = max(
            5,
            size + 3,
        )

        inner_radius = max(
            2,
            size // 2,
        )

        pygame.draw.circle(
            surface,
            color,
            (x, y),
            outer_radius,
            width=max(2, size // 2),
        )

        pygame.draw.circle(
            surface,
            self.palette.soil,
            (x, y),
            inner_radius,
        )

        zzz_color = _blend(
            color,
            (235, 235, 220),
            0.55,
        )

        text = self.font.render(
            "z",
            True,
            zzz_color,
        )

        surface.blit(
            text,
            (
                x + outer_radius,
                y - outer_radius - 5,
            ),
        )

        if size >= 5:
            small_text = self.font.render(
                "z",
                True,
                zzz_color,
            )

            surface.blit(
                small_text,
                (
                    x + outer_radius + 5,
                    y - outer_radius - 15,
                ),
            )

    def _render_sleeping(
        self,
        surface: pygame.Surface,
        worm: Worm,
        x: int,
        y: int,
    ) -> None:
        """Render a sleeping worm."""
        self._render_living(
            surface,
            worm,
            x,
            y,
        )

    def _render_corpse(
        self,
        surface: pygame.Surface,
        worm: Worm,
        x: int,
        y: int,
    ) -> None:
        """Render a corpse becoming progressively darker."""
        fresh_color = _blend(
            self.palette.insect,
            (55, 45, 38),
            0.72,
        )

        rotten_color = (
            28,
            25,
            22,
        )

        color = _blend(
            fresh_color,
            rotten_color,
            worm.rot,
        )

        width = max(
            5,
            int(
                9 * worm.size
            ),
        )

        height = max(
            2,
            int(
                4 * worm.size
            ),
        )

        pygame.draw.ellipse(
            surface,
            color,
            (
                x - width // 2,
                y - height // 2,
                width,
                height,
            ),
        )

        # Small pieces disappear as decomposition progresses.
        if worm.rot < 0.7:
            pygame.draw.circle(
                surface,
                color,
                (
                    x + width // 2,
                    y + 1,
                ),
                max(1, height // 2),
            )

        if worm.rot > 0.55:
            decay_color = _blend(
                color,
                self.palette.soil,
                (worm.rot - 0.55) / 0.45,
            )

            pygame.draw.rect(
                surface,
                decay_color,
                (
                    x - width // 3,
                    y,
                    max(2, width // 4),
                    max(1, height // 2),
                ),
            )