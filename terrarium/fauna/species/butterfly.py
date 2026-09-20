"""Butterfly: diurnal flier; drinks nectar and pollinates flowers."""
from __future__ import annotations

import math

import pygame

from ...palette.color_utils import jitter, modulate, scale
from ..base import InsectSpecies
from ..behaviors.feeding import Feed, NectarFood
from ..behaviors.reproduction import Reproduce
from ..behaviors.resting import Rest
from ..behaviors.wander import FlyWander
from ..registry import register


@register
class Butterfly(InsectSpecies):
    name = "butterfly"
    locomotion = "fly"
    activity_pref = "day"
    hunger_rate = 0.42
    lifespan = (300.0, 480.0)
    mature_age = 40.0
    speed = 8.0
    repro_threshold = 0.7
    repro_cost = 30.0
    repro_cooldown = 55.0
    litter = (1, 2)
    max_population = 24
    initial_count = (5, 9)

    def make_colors(self, palette, rng):
        wing = jitter(rng.choice(palette.butterfly_wings), rng, dh=4)
        return {"body": palette.ant, "wing": wing}

    def build_behaviors(self):
        return [Rest(0.2),
                Feed([NectarFood()], hungry_below=0.88, radius=12, reach=2),
                Reproduce(mate_radius=14),
                FlyWander()]

    def draw(self, surf, ins, sx, sy, cell, light):
        wing = modulate(ins.colors["wing"], light)
        body = modulate(ins.colors["body"], light)
        flap = abs(math.sin(ins.age * 14.0 + ins.id)) if not ins.perched else 0.05
        wh = max(2, int(cell * (0.7 + 0.9 * flap)))
        ww = cell if not ins.perched else max(1, cell // 2)
        if ins.juvenile:
            ww, wh = max(2, ww - 1), max(2, wh - 1)
        pygame.draw.rect(surf, wing, (sx - ww, sy - wh // 2, ww, wh))
        pygame.draw.rect(surf, wing, (sx + 1, sy - wh // 2, ww, wh))
        pygame.draw.rect(surf, scale(wing, 0.7), (sx - ww, sy - wh // 2, 1, wh))
        pygame.draw.rect(surf, scale(wing, 0.7), (sx + ww, sy - wh // 2, 1, wh))
        pygame.draw.rect(surf, body, (sx - 1, sy - cell // 2, 2, cell))
