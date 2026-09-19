"""Base plant entity.

This replacement provides a simpler, more resilient lifecycle for
plants: logistic-style regrowth, clearer consumption API, and a
reproduction cooldown. External code that reads or mutates
`growth` and uses `update()` or `can_reproduce()` remains compatible.
"""

from __future__ import annotations

from dataclasses import dataclass

from config import settings


@dataclass
class Plant:
    """Base state shared by all plants."""

    x: int
    y: int

    age: float = 0.0
    growth: float = 0.0
    variation: float = 0.0

    # per-species tuning — can be overridden by subclasses
    growth_rate: float = 0.08
    max_growth: float = 1.0

    reproduction_timer: float = 0.0

    def __post_init__(self) -> None:
        # deterministic small variation based on position
        if self.variation == 0.0:
            seed = ((self.x * 37) + (self.y * 17) + (self.x * self.y)) % 97
            self.variation = 0.15 + (seed / 97.0) * 0.85

    def update(
        self,
        dt: float,
        daylight: float,
        moisture: float,
        nutrients: float,
    ) -> None:
        """Advance plant growth using environmental conditions.

        Growth follows a simple logistic step so partially eaten plants
        recover more quickly when conditions are good, which helps the
        system recover from overgrazing.
        """
        self.age += dt

        # cooldown ticks down
        self.reproduction_timer = max(0.0, self.reproduction_timer - dt)

        # environmental factors in [0,1]
        light = max(0.0, min(1.0, daylight))
        moist = max(0.0, min(1.0, moisture))
        nutri = max(0.0, min(1.0, nutrients))

        env_factor = light * moist * nutri

        # logistic-like growth: rate * env * (1 - growth/max)
        if env_factor > 0.0 and self.growth < self.max_growth:
            delta = self.growth_rate * env_factor * (1.0 - (self.growth / self.max_growth)) * dt
            self.growth = min(self.max_growth, self.growth + delta)

    def can_reproduce(self) -> bool:
        """Return whether this plant can spread a seed.

        Plants use a configurable maturity threshold and a cooldown so
        they can recover under grazing pressure.
        """
        return self.growth >= settings.PLANT_REPRODUCTION_MATURITY and self.reproduction_timer <= 0.0

    def reproduce(self) -> None:
        """Start reproduction cooldown after seeding."""
        self.reproduction_timer = settings.PLANT_REPRODUCTION_COOLDOWN

    def consume(self, amount: float) -> None:
        """Consume `amount` of growth (0..1). Keeps growth>=0.

        External code also still may mutate `growth` directly; this
        helper exists for clearer semantics.
        """
        self.growth = max(0.0, self.growth - amount)

    @property
    def is_mature(self) -> bool:
        return self.growth >= self.max_growth