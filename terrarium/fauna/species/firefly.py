"""Firefly: nocturnal flier that glows; pollinates flowers after dark."""
from __future__ import annotations

import math

import pygame

from ...palette.color_utils import modulate, scale
from ..base import InsectSpecies
from ..behaviors.feeding import Feed, NectarFood
from ..behaviors.reproduction import Reproduce
from ..behaviors.resting import Rest
from ..behaviors.wander import FlyWander
from ..registry import register

_GLOW_CACHE: dict = {}


def _glow_sprite(color, radius: int):
    key = (color, radius)
    spr = _GLOW_CACHE.get(key)
    if spr is None:
        size = radius * 2 + 1
        spr = pygame.Surface((size, size))
        spr.fill((0, 0, 0))
        for r in range(radius, 0, -1):
            f = (1.0 - r / radius) ** 2 * 0.8
            pygame.draw.circle(spr, scale(color, f), (radius, radius), r)
        _GLOW_CACHE[key] = spr
    return spr


@register
class Firefly(InsectSpecies):
    name = "firefly"
    locomotion = "fly"
    activity_pref = "night"
    hunger_rate = 0.38
    lifespan = (300.0, 480.0)
    mature_age = 40.0
    speed = 5.0
    repro_threshold = 0.7
    repro_cost = 30.0
    repro_cooldown = 55.0
    litter = (1, 2)
    max_population = 26
    initial_count = (6, 10)

    def make_colors(self, palette, rng):
        return {"body": palette.firefly_body, "glow": palette.firefly_glow,
                "wing": scale(palette.firefly_body, 1.5)}

    def build_behaviors(self):
        return [Rest(0.2),
                Feed([NectarFood()], hungry_below=0.88, radius=12, reach=2),
                Reproduce(mate_radius=14),
                FlyWander()]

    def _pulse(self, ins) -> float:
        return 0.55 + 0.45 * math.sin(ins.age * 3.2 + ins.id * 1.7)

    def draw(self, surf, ins, sx, sy, cell, light):
        body = modulate(ins.colors["body"], light)
        pygame.draw.rect(surf, body, (sx - 1, sy - cell // 2, 2, cell - 1))
        if not ins.perched:
            flap = abs(math.sin(ins.age * 30.0 + ins.id))
            pygame.draw.rect(surf, modulate(ins.colors["wing"], light), (sx - 3, sy - cell // 2 - 1, 2, 1 + int(flap * 2)))
            pygame.draw.rect(surf, modulate(ins.colors["wing"], light), (sx + 1, sy - cell // 2 - 1, 2, 1 + int(flap * 2)))
        glow = scale(ins.colors["glow"], 0.45 + 0.55 * self._pulse(ins))
        pygame.draw.rect(surf, glow, (sx - 1, sy + cell // 2 - 1, 2, 2))

    def draw_glow(self, surf, ins, sx, sy, cell, night):
        if night < 0.05:
            return
        k = night * (0.35 if ins.perched else 1.0) * (0.35 + 0.65 * self._pulse(ins))
        radius = max(6, cell * 4)
        spr = _glow_sprite(scale(ins.colors["glow"], k), radius)
        surf.blit(spr, (sx - radius, sy + cell // 2 - radius), special_flags=pygame.BLEND_RGB_ADD)
