"""Beetle: night-time herbivore and decomposer that climbs plants and burrows a little."""
from __future__ import annotations

import pygame

from ...palette.color_utils import jitter, modulate, scale
from ..base import InsectSpecies
from ..behaviors.digging import SoilMover
from ..behaviors.feeding import DetritusFood, Feed, PlantFood
from ..behaviors.reproduction import Reproduce
from ..behaviors.wander import CrawlWander
from ..registry import register


@register
class Beetle(InsectSpecies):
    name = "beetle"
    locomotion = "crawl"
    activity_pref = "night"
    min_activity = 0.25
    hunger_rate = 0.42
    lifespan = (450.0, 760.0)
    mature_age = 55.0
    speed = 4.0
    repro_threshold = 0.72
    repro_cost = 34.0
    repro_cooldown = 80.0
    litter = (1, 2)
    max_population = 34
    initial_count = (6, 10)
    can_dig = True

    def make_colors(self, palette, rng):
        shell = jitter(rng.choice(palette.beetle_shells), rng, dh=5)
        return {"body": shell, "shell": shell}

    def build_behaviors(self):
        return [Feed([PlantFood(9.0), DetritusFood(8.0)], hungry_below=0.8, radius=10),
                Reproduce(),
                SoilMover(dig_chance=0.025, max_depth=6),
                CrawlWander()]

    def draw(self, surf, ins, sx, sy, cell, light):
        shell = modulate(ins.colors["shell"], light)
        dark = scale(shell, 0.55)
        if ins.juvenile:
            pygame.draw.rect(surf, dark, (sx + 1, sy + cell // 2, cell - 2, cell // 2))
            pygame.draw.rect(surf, shell, (sx + 1, sy + cell // 2, cell - 3, max(1, cell // 2 - 1)))
            return
        pygame.draw.rect(surf, dark, (sx, sy, cell + 1, cell))
        pygame.draw.rect(surf, shell, (sx + 1, sy + 1, cell - 1, cell - 2))
        pygame.draw.rect(surf, scale(shell, 1.4), (sx + 1, sy + 1, 1, 1))
