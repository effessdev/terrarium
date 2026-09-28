"""Heads-up display: stats panel, help icon and help panel."""
from __future__ import annotations

import pygame

HELP_LINES = [
    "Controls",
    "  Left mouse      paint with the selected tool",
    "  Right mouse     erase",
    "  Mouse wheel     brush size",
    "  1-7             select tool: sand soil water rock erase plant insect",
    "  SPACE           pause / resume",
    "  + / -           simulation speed",
    "  H               show / hide this HUD",
    "  ? icon or F1    show / hide help",
    "  R               new world",
    "  S               screenshot",
    "  ESC             quit",
]
HELP_LINE_H, PANEL_PAD, MARGIN = 16, 8, 10
# ICON_SS = supersampling factor for a smooth circle
ICON_SIZE, ICON_HITBOX, ICON_SS = 26, 34, 4


class Hud:
    def __init__(self) -> None:
        self.font = pygame.font.Font(None, 20)
        self.icon_font = pygame.font.Font(None, 20 * ICON_SS)
        self.cache: list = []
        self.last = -99
        self.help_surf: pygame.Surface | None = None
        self.help_key: tuple | None = None
        self.icon_rect = pygame.Rect(0, 0, ICON_HITBOX, ICON_HITBOX)

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

    def _panel(self, w, h, pal) -> pygame.Surface:
        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        panel.fill((*pal.ui_panel, 150))
        return panel

    def _build_help(self, pal) -> pygame.Surface:
        rows = [self.font.render(t, True, pal.ui_text) for t in HELP_LINES]
        w = max(t.get_width() for t in rows) + 2 * PANEL_PAD
        h = 2 * PANEL_PAD + \
            sum(max(t.get_height(), HELP_LINE_H) + 2 for t in rows)
        panel = self._panel(w, h, pal)
        y = PANEL_PAD
        for surf in rows:
            panel.blit(surf, (PANEL_PAD, y))
            y += max(surf.get_height(), HELP_LINE_H) + 2
        return panel

    def _draw_help_panel(self, screen, app) -> None:
        # rebuild on toggle / new world
        if self.help_key != (app.show_help, app.sim.ctx.palette.name):
            self.help_key = (app.show_help, app.sim.ctx.palette.name)
            self.help_surf = self._build_help(app.sim.ctx.palette)
        if self.help_surf is None:
            return
        x = screen.get_width() - MARGIN - self.help_surf.get_width()
        screen.blit(self.help_surf, (x, self.icon_rect.bottom + 6))

    def _draw_icon(self, screen, app) -> None:
        pal = app.sim.ctx.palette
        fill, ink = (pal.ui_text, pal.ui_panel) if app.show_help else (
            pal.ui_panel, pal.ui_text)
        r = ICON_SIZE * ICON_SS // 2
        # supersampled, smoothed on scale-down
        icon = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(icon, (*fill, 150), (r, r), r - ICON_SS)
        q = self.icon_font.render("?", True, ink)
        icon.blit(q, (r - q.get_width() // 2, r - q.get_height() // 2))
        icon = pygame.transform.smoothscale(icon, (ICON_SIZE, ICON_SIZE))
        screen.blit(icon, icon.get_rect(center=self.icon_rect.center))

    def draw(self, screen, app) -> None:
        self.icon_rect.center = (screen.get_width() - MARGIN - ICON_HITBOX // 2,
                                 MARGIN + ICON_HITBOX // 2)
        now = pygame.time.get_ticks()
        if now - self.last > 250:
            self.last = now
            pal = app.sim.ctx.palette
            self.cache = [self.font.render(t, True, pal.ui_text)
                          for t in self._lines(app)]
        if self.cache:
            w = max(t.get_width() for t in self.cache) + 14
            h = len(self.cache) * 16 + 10
            screen.blit(self._panel(w, h, app.sim.ctx.palette),
                        (MARGIN, MARGIN))
            for i, t in enumerate(self.cache):
                screen.blit(t, (MARGIN + 7, MARGIN + 5 + i * 16))
        self._draw_icon(screen, app)
        if app.show_help:
            self._draw_help_panel(screen, app)
