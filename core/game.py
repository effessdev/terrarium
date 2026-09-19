"""Main Pygame application."""

from __future__ import annotations

import pygame

from config import settings
from core.clock import SimulationClock
from rendering.terrain_renderer import TerrainRenderer
from utils.randomizer import Randomizer
from world.world import World


class Game:
    """Owns the application loop and high-level systems."""

    def __init__(self) -> None:
        pygame.init()

        self.screen = pygame.display.set_mode(
            (
                settings.WINDOW_WIDTH,
                settings.WINDOW_HEIGHT,
            )
        )

        pygame.display.set_caption(
            settings.WINDOW_TITLE
        )

        self.render_clock = pygame.time.Clock()

        self.simulation_clock = SimulationClock(
            settings.SIMULATION_HZ
        )

        self.randomizer = Randomizer()

        self.world = World(
            settings.WORLD_WIDTH,
            settings.WORLD_HEIGHT,
            self.randomizer,
        )

        self.terrain_renderer = TerrainRenderer()

        self.font = pygame.font.Font(
            None,
            24,
        )

        self.running = False

    def run(self) -> None:
        """Run the application until the user exits."""
        self.running = True

        while self.running:
            self.simulation_clock.tick()

            self._handle_events()
            self._update_simulation()
            self._render()

            self.render_clock.tick(
                settings.TARGET_FPS
            )

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
            and steps
            < settings.MAX_SIMULATION_STEPS_PER_FRAME
        ):
            self._simulation_step(
                self.simulation_clock.fixed_dt
            )

            self.simulation_clock.consume_step()

            steps += 1

    def _simulation_step(self, dt: float) -> None:
        """Advance all world-level simulation systems."""
        self.world.update(dt)

    def _render(self) -> None:
        """Render the current world."""
        self.terrain_renderer.render(
            self.screen,
            self.world,
        )

        if settings.SHOW_DEBUG_INFO:
            self._draw_debug_info()

        pygame.display.flip()

    def _draw_debug_info(self) -> None:
        """Draw basic runtime information."""
        fps = self.render_clock.get_fps()

        lines = [
            f"FPS: {fps:.1f}",
            f"Seed: {self.randomizer.seed}",
            (
                "World: "
                f"{self.world.width}x"
                f"{self.world.height}"
            ),
            (
                "Simulation: "
                f"{self.simulation_clock.total_simulation_time:.1f}s"
            ),
            "ESC - Quit",
        ]

        x = 15
        y = 15

        for line in lines:
            text = self.font.render(
                line,
                True,
                (220, 225, 220),
            )

            self.screen.blit(
                text,
                (x, y),
            )

            y += 24

    @staticmethod
    def _shutdown() -> None:
        """Cleanly shut down Pygame."""
        pygame.quit()