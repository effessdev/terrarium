"""Ant: scavenger and excavator.  Digs tunnels, hauls soil to the surface, eats corpses,
seeds and rot.  The main engine behind moving terrain."""
from __future__ import annotations

import pygame

from ...palette.color_utils import jitter, modulate, scale
from ...world.materials import SAND
from ..base import InsectSpecies
from ..behaviors.digging import SoilMover
from ..behaviors.feeding import CorpseFood, DetritusFood, Feed, SeedFood
from ..behaviors.locomotion import DIRS
from ..behaviors.reproduction import Reproduce
from ..behaviors.wander import CrawlWander
from ..registry import register


@register
class Ant(InsectSpecies):
    name = "ant"
    locomotion = "crawl"
    activity_pref = "any"
    hunger_rate = 0.5
    lifespan = (420.0, 700.0)
    mature_age = 45.0
    speed = 6.0
    repro_threshold = 0.72
    repro_cost = 32.0
    repro_cooldown = 60.0
    litter = (1, 2)
    max_population = 48
    initial_count = (10, 16)
    can_dig = True

    def make_colors(self, palette, rng):
        body = jitter(palette.ant, rng, dh=5, dv=0.03)
        return {"body": body, "head": scale(body, 1.35), "sand": palette.sand, "soil": palette.soil}

    def build_behaviors(self):
        return [Feed([CorpseFood(), SeedFood(), DetritusFood()], hungry_below=0.7, radius=10),
                Reproduce(),
                SoilMover(dig_chance=0.12, max_depth=18),
                CrawlWander()]

    def draw(self, surf, ins, sx, sy, cell, light):
        q = max(1, cell // 4)
        body = modulate(ins.colors["body"], light)
        if ins.juvenile:
            pygame.draw.rect(surf, body, (sx + q, sy + 2 * q, cell - 2 * q, cell - 2 * q))
            return
        pygame.draw.rect(surf, body, (sx, sy + q, cell, cell - q))
        fx = DIRS[ins.dir_idx][0]
        hx = sx + (cell - 2 * q if fx >= 0 else 0)
        pygame.draw.rect(surf, modulate(ins.colors["head"], light), (hx, sy, 2 * q, 2 * q))
        if ins.carry is not None:
            key = "sand" if ins.carry[0] == SAND else "soil"
            pygame.draw.rect(surf, modulate(ins.colors[key], light), (sx + q, sy - q, 2 * q, 2 * q))
