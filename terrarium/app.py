"""Application shell: window, fixed-timestep loop, rendering, input."""
from __future__ import annotations

import time

import pygame

from .builder import build_simulation
from .config import Config
from .render.renderer import Renderer
from .ui.hud import Hud
from .ui.input import InputController
from .ui.tools import TOOLS


class App:
    def __init__(self, config: Config | None = None, seed: int | None = None) -> None:
        self.config = config or Config()
        pygame.display.init()
        pygame.font.init()
        w = self.config.window
        self.screen = pygame.display.set_mode((w.width, w.height))
        pygame.display.set_caption(w.title)
        self.clock = pygame.time.Clock()
        self.input = InputController(self)
        self.speed_index = self.config.time.default_speed_index
        self.tool = TOOLS[0]
        self.brush = 2
        self.show_hud = self.config.render.show_hud
        self.show_help = False
        self.running = True
        self.fps = 0.0
        self.new_world(seed)

    def new_world(self, seed: int | None = None) -> None:
        self.sim = build_simulation(self.config, seed)
        self.renderer = Renderer(self.sim.ctx, self.screen)
        self.hud = Hud(self.sim.ctx)
        self.accum = 0.0
        print(f"[terrarium] {self.sim.ctx.palette.name} | {self.sim.ctx.params.describe} | seed {self.sim.ctx.rng.seed}")

    def toggle_pause(self) -> None:
        self.speed_index = 0 if self.speed_index else self.config.time.default_speed_index

    def change_speed(self, d: int) -> None:
        n = len(self.config.time.speeds)
        self.speed_index = max(0, min(n - 1, self.speed_index + d))

    def screenshot(self) -> None:
        name = f"terrarium_{self.sim.ctx.rng.seed}_{int(time.time())}.png"
        pygame.image.save(self.screen, name)
        print("saved", name)

    def step(self, frame_dt: float) -> None:
        tc = self.config.time
        speed = tc.speeds[self.speed_index]
        self.accum += min(frame_dt, 0.25) * speed
        tick_dt = self.config.tick_dt
        n = 0
        while self.accum >= tick_dt and n < tc.max_ticks_per_frame:
            self.sim.tick()
            self.accum -= tick_dt
            n += 1
        if n == tc.max_ticks_per_frame:
            self.accum = 0.0                      # cannot keep up: drop the backlog

    def run(self) -> None:
        while self.running:
            frame_dt = self.clock.tick(self.config.window.fps_cap) / 1000.0
            self.fps = self.clock.get_fps()
            for e in pygame.event.get():
                self.input.handle(e)
            self.input.poll_mouse()
            self.step(frame_dt)
            self.renderer.draw()
            if self.show_hud:
                self.hud.draw(self.screen, self)
            pygame.display.flip()
        pygame.quit()
