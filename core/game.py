"""Main Pygame application."""

from __future__ import annotations

import pygame

from config import settings
from config.palette import PaletteGenerator
from core.clock import SimulationClock
from core.day_night import DayNightCycle
from rendering.plant_renderer import PlantRenderer
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

        self.simulation_speed = settings.DEFAULT_SIMULATION_SPEED

        self.randomizer = Randomizer()

        palette_generator = PaletteGenerator(
            self.randomizer
        )

        self.palette = palette_generator.generate()

        self.day_night = DayNightCycle(
            settings.DAY_LENGTH_SECONDS
        )

        self.world = World(
            settings.WORLD_WIDTH,
            settings.WORLD_HEIGHT,
            self.randomizer,
        )

        self.terrain_renderer = TerrainRenderer(
            self.palette,
            self.day_night,
        )

        self.plant_renderer = PlantRenderer(
            self.palette,
        )

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

    def _change_simulation_speed(
        self,
        direction: int,
    ) -> None:
        """Move through the available simulation speeds."""
        speeds = settings.SIMULATION_SPEEDS

        try:
            current_index = speeds.index(
                self.simulation_speed
            )
        except ValueError:
            current_index = 1

        new_index = max(
            0,
            min(
                len(speeds) - 1,
                current_index + direction,
            ),
        )

        self.simulation_speed = speeds[new_index]


    def _set_simulation_speed(
        self,
        speed: float,
    ) -> None:
        """Set the simulation speed if it is supported."""
        if speed in settings.SIMULATION_SPEEDS:
            self.simulation_speed = speed

    def _handle_events(self) -> None:
        """Process Pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                elif event.key == pygame.K_0:
                    self._set_simulation_speed(0.0)

                elif event.key == pygame.K_1:
                    self._set_simulation_speed(1.0)

                elif event.key == pygame.K_2:
                    self._set_simulation_speed(2.0)

                elif event.key == pygame.K_3:
                    self._set_simulation_speed(4.0)

                elif event.key == pygame.K_4:
                    self._set_simulation_speed(8.0)

                elif event.key == pygame.K_5:
                    self._set_simulation_speed(16.0)

                elif event.key in {
                    pygame.K_EQUALS,
                    pygame.K_KP_PLUS,
                }:
                    self._change_simulation_speed(1)

                elif event.key in {
                    pygame.K_MINUS,
                    pygame.K_KP_MINUS,
                }:
                    self._change_simulation_speed(-1)

    def _update_simulation(self) -> None:
        """Advance the simulation using a fixed timestep."""
        steps = 0

        while (
            self.simulation_clock.should_step()
            and steps
            < settings.MAX_SIMULATION_STEPS_PER_FRAME
        ):
            dt = (
                self.simulation_clock.fixed_dt
                * self.simulation_speed
            )

            if self.simulation_speed > 0.0:
                self._simulation_step(dt)

            self.simulation_clock.consume_step()

            steps += 1

    def _simulation_step(self, dt: float) -> None:
        """Advance all world-level simulation systems."""
        self.day_night.update(dt)

        self._update_plants(dt)

        self.world.update(dt)

    def _update_plants(self, dt: float) -> None:
        """Update plant growth."""
        for plant in self.world.plants:
            moisture = self.world.terrain[
                plant.y
            ][plant.x].moisture

            nutrients = self.world.terrain[
                plant.y
            ][plant.x].nutrients

            plant.update(
                dt,
                self.day_night.daylight,
                moisture,
                nutrients,
            )

    def _render(self) -> None:
        """Render the current world."""
        self.terrain_renderer.render(
            self.screen,
            self.world,
        )

        self.plant_renderer.render(
            self.screen,
            self.world.plants,
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
                "Plants: "
                f"{len(self.world.plants)}"
            ),
            (
                "Simulation: "
                f"{self.simulation_clock.total_simulation_time:.1f}s"
            ),
            (
                "Time: "
                f"{self.day_night.formatted_time()}"
            ),
            (
                f"Speed: "
                f"{self.simulation_speed:g}x"
            ),
            (
                "Daylight: "
                f"{self.day_night.daylight:.2f}"
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
                (x, y)
            )

            y += 24

    @staticmethod
    def _shutdown() -> None:
        """Cleanly shut down Pygame."""
        pygame.quit()