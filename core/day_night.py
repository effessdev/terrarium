"""Day and night cycle."""

from __future__ import annotations

import math


class DayNightCycle:
    """Controls the simulated time of day."""

    def __init__(self, day_length_seconds: float) -> None:
        if day_length_seconds <= 0:
            raise ValueError(
                "day_length_seconds must be greater than zero"
            )

        self.day_length_seconds = day_length_seconds
        self.time_seconds = 0.0

    @property
    def normalized_time(self) -> float:
        """
        Return the current time as 0.0 - 1.0.

        0.00 = midnight
        0.25 = sunrise
        0.50 = noon
        0.75 = sunset
        1.00 = midnight
        """
        return (
            self.time_seconds
            / self.day_length_seconds
        )

    @property
    def hour(self) -> float:
        """Return the simulated hour, from 0 to <24."""
        return self.normalized_time * 24.0

    @property
    def is_day(self) -> bool:
        """Return whether the sun is above the horizon."""
        return 6.0 <= self.hour < 18.0

    @property
    def daylight(self) -> float:
        """
        Return a smooth daylight factor.

        0.0 = full night
        1.0 = full daylight
        """
        angle = (
            self.normalized_time * math.tau
        )

        # Shift the sine wave so maximum daylight
        # occurs at noon.
        value = math.sin(angle - math.pi / 2)

        return max(
            0.0,
            (value + 1.0) / 2.0,
        )

    def update(self, dt: float) -> None:
        """Advance the simulated time."""
        self.time_seconds += dt

        if self.time_seconds >= self.day_length_seconds:
            self.time_seconds %= self.day_length_seconds

    def formatted_time(self) -> str:
        """Return a readable simulated clock."""
        total_minutes = int(
            self.hour * 60
        )

        hours = (
            total_minutes // 60
        ) % 24

        minutes = total_minutes % 60

        return f"{hours:02d}:{minutes:02d}"