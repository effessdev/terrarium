"""Main Pygame application."""

from __future__ import annotations

import pygame

from config import settings
from core.clock import SimulationClock
from utils.randomizer import Randomizer


class Game:
    """Owns the application loop and high-level systems."""

    def __init__(self) -> None:
        pygame.init()

        self.screen = pygame.display.set_mode(
            (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
        )

        pygame.display.set_caption(settings.WINDOW_TITLE)

        self.render_clock = pygame.time.Clock()
        self.simulation_clock = SimulationClock(settings.SIMULATION_HZ)

        self.randomizer = Randomizer()

        self.font = pygame.font.Font(None, 24)

        self.running = False

    def run(self) -> None:
        """Run the application until the user exits."""
        self.running = True

        while self.running:
            self.simulation_clock.tick()

            self._handle_events()
            self._update_simulation()
            self._render()

            self.render_clock.tick(settings.TARGET_FPS)

        self._shutdown()

    def _handle_events(self) -> None:
        """Process Pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def _update_simulation(self) -> None:
        """Advance the simulation using a fixed timestep."""
        steps = 0

        while (
            self.simulation_clock.should_step()
            and steps < settings.MAX_SIMULATION_STEPS_PER_FRAME
        ):
            self._simulation_step(
                self.simulation_clock.fixed_dt
            )

            self.simulation_clock.consume_step()
            steps += 1

    def _simulation_step(self, dt: float) -> None:
        """
        Perform one simulation step.

        Future simulation systems will be called here.

        Examples:
            water.update(...)
            plants.update(...)
            insects.update(...)
        """
        _ = dt

    def _render(self) -> None:
        """Render the current application state."""
        self.screen.fill(settings.BACKGROUND_COLOR)

        self._draw_title()

        if settings.SHOW_DEBUG_INFO:
            self._draw_debug_info()

        pygame.display.flip()

    def _draw_title(self) -> None:
        """Draw the temporary Phase 1 title."""
        title_font = pygame.font.Font(None, 64)

        text = title_font.render(
            "TERRARIUM",
            True,
            (210, 220, 210),
        )

        text_rect = text.get_rect(
            center=(
                settings.WINDOW_WIDTH // 2,
                settings.WINDOW_HEIGHT // 2,
            )
        )

        self.screen.blit(text, text_rect)

    def _draw_debug_info(self) -> None:
        """Draw basic runtime information."""
        fps = self.render_clock.get_fps()

        lines = [
            f"FPS: {fps:.1f}",
            f"Seed: {self.randomizer.seed}",
            f"Simulation: {self.simulation_clock.total_simulation_time:.1f}s",
            "ESC - Quit",
        ]

        x = 15
        y = 15

        for line in lines:
            text = self.font.render(
                line,
                True,
                (190, 200, 195),
            )

            self.screen.blit(text, (x, y))
            y += 24

    @staticmethod
    def _shutdown() -> None:
        """Cleanly shut down Pygame."""
        pygame.quit()
