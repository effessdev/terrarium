"""Heads-up display: stats panel and help text."""
from __future__ import annotations

import pygame

HELP = ["SPACE pause   +/- speed   H hud   F1 help", "R new world   S screenshot   ESC quit",
        "1-7 tool: sand soil water rock erase plant insect", "Left mouse paint   Right mouse erase   wheel = brush"]


class Hud:
    def __init__(self, ctx) -> None:
        self.ctx = ctx
        self.font = pygame.font.Font(None, 20)
        self.cache: list = []
        self.last = -99

    def _lines(self, app):
        ctx = app.sim.ctx
        s, c = ctx.stats, ctx.clock
        hh, mm = int(c.hour), int((c.hour % 1) * 60)
        sp = ctx.config.time.speeds[app.speed_index]
        pl = " ".join(f"{k[:4]}:{v}" for k, v in s.get("plants", {}).items())
        ins = " ".join(f"{k[:4]}:{v}" for k, v in s.get("insects", {}).items())
        return [f"{ctx.palette.name} / {ctx.params.describe}   seed {ctx.rng.seed}",
                f"Day {c.day + 1}  {hh:02d}:{mm:02d}   speed x{sp:g}{'  PAUSED' if sp == 0 else ''}   FPS {app.fps:.0f}",
                f"Plants {s.get('plant_total', 0)}: {pl}", f"Insects {s.get('insect_total', 0)}: {ins}",
                f"Water cells {s.get('water_cells', 0)}  drips {s.get('drips', 0)}  seeds {s.get('seeds', 0)}",
                f"Tool: {app.tool.name} (brush {app.brush})"]

    def draw(self, screen, app) -> None:
        now = pygame.time.get_ticks()
        if now - self.last > 250:
            self.last = now
            lines = self._lines(app) + (HELP if app.show_help else [])
            pal = app.sim.ctx.palette
            self.cache = [self.font.render(t, True, pal.ui_text) for t in lines]
        if not self.cache:
            return
        w = max(t.get_width() for t in self.cache) + 14
        h = len(self.cache) * 16 + 10
        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        panel.fill((*app.sim.ctx.palette.ui_panel, 150))
        screen.blit(panel, (10, 10))
        for i, t in enumerate(self.cache):
            screen.blit(t, (17, 15 + i * 16))
