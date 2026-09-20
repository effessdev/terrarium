"""Slowly varying weather: cloudiness (sunniness) and temperature.

Published attributes: ``sunniness`` (0.35-1), ``temperature`` (0-1), ``light_level`` (0-1).
A fresh sunniness target is drawn every dawn, so consecutive days differ.
"""
from __future__ import annotations

from ..core.system import System


class Weather(System):
    name = "weather"
    interval = 5

    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        lo = ctx.config.climate.min_sunniness
        self._lo = lo
        self.sunniness = ctx.rng.uniform(0.7, 1.0)
        self._target = self.sunniness
        self.warmth = ctx.rng.uniform(-0.06, 0.06)
        self.temperature = 0.5
        self.light_level = 0.0
        ctx.bus.subscribe("dawn", self._new_day_weather)

    def _new_day_weather(self) -> None:
        rng = self.ctx.rng
        self._target = rng.uniform(self._lo, 1.0)
        self.warmth = max(-0.12, min(0.12, self.warmth + rng.uniform(-0.05, 0.05)))

    def update(self, dt: float) -> None:
        clock = self.ctx.clock
        self.sunniness += (self._target - self.sunniness) * min(1.0, dt * 0.5)
        sun = clock.daylight * (0.55 + 0.45 * self.sunniness)
        self.light_level = clock.daylight * (0.4 + 0.6 * self.sunniness)
        self.temperature = max(0.0, min(1.0, 0.24 + 0.46 * sun + self.warmth
                                        + self.ctx.params.warmth_bias))
