"""``InsectSpecies``: stats + AI recipe + drawing code of one kind of insect.

An insect's AI is an *ordered list of behaviours* (see ``fauna/behaviors``).  Each tick
(or each "step" for crawlers) the first behaviour that returns ``True`` wins, so the list
reads like a priority list: e.g. ``[Feed, Reproduce, SoilMover, Wander]``.
To create a species: subclass, fill in the numbers, list behaviours, implement ``draw``.
"""
from __future__ import annotations


def clamp(v, lo=0.0, hi=1.0):
    return lo if v < lo else hi if v > hi else v


class InsectSpecies:
    name = "insect"
    locomotion = "crawl"            # "crawl" (grid steps) or "fly" (continuous)
    activity_pref = "any"           # "day", "night" or "any"
    min_activity = 0.0              # never sleeps completely when > 0

    max_energy = 100.0
    hunger_rate = 0.5               # energy lost per second
    lifespan = (400.0, 700.0)
    mature_age = 50.0
    speed = 5.0                     # crawl steps / second, or flight cells / second

    repro_threshold = 0.7           # fraction of max energy needed to breed
    repro_cost = 30.0
    repro_cooldown = 70.0
    litter = (1, 2)
    max_population = 40
    initial_count = (6, 12)
    can_dig = False

    # ---- hooks --------------------------------------------------------------
    def make_colors(self, palette, rng) -> dict:
        raise NotImplementedError

    def build_behaviors(self) -> list:
        raise NotImplementedError

    def draw(self, surf, ins, sx: int, sy: int, cell: int, light) -> None:
        """Draw onto the screen.  (sx, sy) is the top-left pixel of the insect's cell."""
        raise NotImplementedError

    def draw_glow(self, surf, ins, sx: int, sy: int, cell: int, night: float) -> None:
        """Optional additive glow pass, called after tinting (fireflies use it)."""

    # ---- shared logic -----------------------------------------------------------
    def activity_level(self, ctx) -> float:
        d = ctx.clock.daylight
        if self.activity_pref == "day":
            a = d
        elif self.activity_pref == "night":
            a = 1.0 - d
        else:
            a = 0.8
        a = clamp(a * 1.6)
        a = max(a, self.min_activity)
        return a * clamp(0.35 + ctx.weather.temperature * 1.3, 0.3, 1.0)
