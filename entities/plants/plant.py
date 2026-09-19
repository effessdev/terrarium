"""Base plant entity."""

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

    growth_rate: float = 0.08
    max_growth: float = 1.0

    reproduction_timer: float = 0.0

    def update(
        self,
        dt: float,
        daylight: float,
        moisture: float,
        nutrients: float,
    ) -> None:
        """Advance plant growth using environmental conditions."""
        self.age += dt

        self.reproduction_timer = max(
            0.0,
            self.reproduction_timer - dt,
        )

        light_factor = max(
            0.0,
            min(1.0, daylight),
        )

        moisture_factor = max(
            0.0,
            min(1.0, moisture),
        )

        nutrient_factor = max(
            0.0,
            min(1.0, nutrients),
        )

        growth_factor = (
            light_factor
            * moisture_factor
            * nutrient_factor
        )

        self.growth += (
            self.growth_rate
            * growth_factor
            * dt
        )

        self.growth = min(
            self.growth,
            self.max_growth,
        )

    def can_reproduce(self) -> bool:
        """Return whether this plant can currently spread."""
        return (
            self.growth >= self.max_growth
            and self.reproduction_timer <= 0.0
        )

    def reproduce(self) -> None:
        """Start the reproduction cooldown."""
        self.reproduction_timer = (
            settings.PLANT_REPRODUCTION_COOLDOWN
        )

    @property
    def is_mature(self) -> bool:
        """Return whether the plant has reached full growth."""
        return self.growth >= self.max_growth