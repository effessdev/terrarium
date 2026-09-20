"""Day/night cycle.

``phase`` runs 0..1 with 0 = midnight, 0.25 = sunrise, 0.5 = noon, 0.75 = sunset.
Published attributes (read by renderer, plants, insects, weather ...):
    phase, day, hour, sun_height (-1..1), daylight (0..1), is_day, sun_u, moon_u
Emits ``dawn`` / ``dusk`` / ``new_day`` on the event bus.
"""
from __future__ import annotations

import math

from ..core.system import System


def smoothstep(a: float, b: float, x: float) -> float:
    if a == b:
        return 0.0 if x < a else 1.0
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


class DayClock(System):
    name = "clock"
    interval = 1

    def __init__(self, ctx, start_phase: float = 0.3) -> None:
        super().__init__(ctx)
        self.day_length = ctx.config.time.day_length
        self.start_phase = start_phase
        self.day = 0
        self._was_day = None
        self._compute(0.0)
        self._was_day = self.is_day

    def _compute(self, t: float) -> None:
        total = t / self.day_length + self.start_phase
        self.day = int(total)
        self.phase = total % 1.0
        self.hour = self.phase * 24.0
        self.sun_height = math.sin(2 * math.pi * (self.phase - 0.25))
        self.daylight = smoothstep(-0.08, 0.35, self.sun_height)
        self.is_day = self.daylight > 0.25
        self.sun_u = (self.phase - 0.25) / 0.5                    # 0..1 while the sun is up
        self.moon_u = (((self.phase + 0.5) % 1.0) - 0.25) / 0.5   # 0..1 while the moon is up

    def update(self, dt: float) -> None:
        prev_day = self.day
        self._compute(self.ctx.time)
        bus = self.ctx.bus
        if self._was_day is not None and self.is_day != self._was_day:
            bus.emit("dawn" if self.is_day else "dusk")
        self._was_day = self.is_day
        if self.day != prev_day:
            bus.emit("new_day", day=self.day)

    # helpers ----------------------------------------------------------
    def phase_weights(self):
        """(day_w, night_w, twilight_w, is_morning) weights that always sum to 1."""
        h = self.sun_height
        day_w = smoothstep(0.0, 0.45, h)
        night_w = 1.0 - smoothstep(-0.40, 0.0, h)
        twi = max(0.0, 1.0 - day_w - night_w)
        return day_w, night_w, twi, self.phase < 0.5
