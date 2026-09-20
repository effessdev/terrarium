"""Input handling: translates pygame events into app commands."""
from __future__ import annotations

import pygame

from .tools import TOOLS


class InputController:
    def __init__(self, app) -> None:
        self.app = app

    def handle(self, event) -> None:
        a = self.app
        if event.type == pygame.QUIT:
            a.running = False
        elif event.type == pygame.KEYDOWN:
            k = event.key
            if k == pygame.K_ESCAPE:
                a.running = False
            elif k == pygame.K_SPACE:
                a.toggle_pause()
            elif k in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                a.change_speed(1)
            elif k in (pygame.K_MINUS, pygame.K_KP_MINUS):
                a.change_speed(-1)
            elif k == pygame.K_h:
                a.show_hud = not a.show_hud
            elif k == pygame.K_F1:
                a.show_help = not a.show_help
            elif k == pygame.K_r:
                a.new_world()
            elif k == pygame.K_s:
                a.screenshot()
            else:
                for t in TOOLS:
                    if k == ord(t.key):
                        a.tool = t
        elif event.type == pygame.MOUSEWHEEL:
            a.brush = max(1, min(8, a.brush + event.y))

    def poll_mouse(self) -> None:
        a = self.app
        b = pygame.mouse.get_pressed()
        if not (b[0] or b[2]):
            return
        cell = a.config.window.cell_size
        mx, my = pygame.mouse.get_pos()
        x, y = mx // cell, my // cell
        tool = a.tool if b[0] else next(t for t in TOOLS if t.name == 'Erase')
        tool.apply(a.sim.ctx, x, y, a.brush)
