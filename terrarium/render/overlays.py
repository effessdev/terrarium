"""Full-resolution overlays drawn after the low-res world is scaled up."""
from __future__ import annotations

import pygame

from ..palette.color_utils import modulate
from .common import light_tint


class EntityOverlay:
    """Insects and corpses (smooth sub-cell positions for fliers) + firefly glow."""
    def __init__(self, ctx) -> None:
        self.ctx = ctx

    def draw(self, screen) -> None:
        ctx = self.ctx
        cell = ctx.config.window.cell_size
        light = light_tint(ctx)
        for c in ctx.corpses.corpses:
            k = min(1.0, c.age / ctx.corpses.ROT_TIME)
            col = modulate(tuple(int(c[0] * (1 - 0.6 * k) + 70 * 0.6 * k) for c in [(v,) for v in c.color]), light)
            pygame.draw.rect(screen, col, (c.x * cell + 1, c.y * cell + cell // 2, cell - 2, cell // 2))
        for i in ctx.fauna.insects:
            sp = i.species
            if sp.locomotion == "fly":
                sx, sy = int(i.x * cell), int(i.y * cell)
            else:
                sx, sy = int(i.x) * cell, int(i.y) * cell
            sp.draw(screen, i, sx, sy, cell, light)
        night = 1.0 - ctx.clock.daylight
        if night > 0.05:
            for i in ctx.fauna.insects:
                if i.species.locomotion == "fly":
                    i.species.draw_glow(screen, i, int(i.x * cell), int(i.y * cell), cell, night)


class GlassOverlay:
    """Terrarium glass: rim highlights, reflections and condensation droplets on the lid."""
    def __init__(self, ctx, size) -> None:
        self.ctx = ctx
        w, h = size
        self.size = size
        p = ctx.palette
        self.edge = p.glass_edge
        self.glare = pygame.Surface((w, h))
        self.glare.fill((0, 0, 0))
        s = (14, 14, 16)
        pygame.draw.polygon(self.glare, s, [(w * 0.08, 0), (w * 0.14, 0), (w * 0.05, h * 0.55), (w * 0.0, h * 0.55)])
        pygame.draw.polygon(self.glare, (9, 9, 11), [(w * 0.17, 0), (w * 0.19, 0), (w * 0.10, h * 0.55), (w * 0.08, h * 0.55)])
        self.glare = self.glare.subsurface((0, 0, int(w * 0.3), int(h * 0.6))).copy()

    def draw(self, screen) -> None:
        ctx = self.ctx
        cell = ctx.config.window.cell_size
        w, h = self.size
        screen.blit(self.glare, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        drops = ctx.water_cycle.lid_drops
        col = (225, 240, 250)
        for x in (drops > 0.12).nonzero()[0]:
            r = max(1, int(drops[x] * cell * 0.9))
            pygame.draw.circle(screen, col, (int(x) * cell + cell // 2, cell + r // 2), r)
        pygame.draw.rect(screen, self.edge, (0, 0, w, h), 3)
