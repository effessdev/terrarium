"""Procedural terrarium color palettes."""

from __future__ import annotations

import colorsys
from dataclasses import dataclass

from utils.randomizer import Randomizer


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _hsv_to_rgb(
    hue: float,
    saturation: float,
    value: float,
) -> tuple[int, int, int]:
    """Convert normalized HSV values to an RGB tuple."""
    red, green, blue = colorsys.hsv_to_rgb(
        hue % 1.0,
        _clamp(saturation),
        _clamp(value),
    )

    return (
        int(red * 255),
        int(green * 255),
        int(blue * 255),
    )


@dataclass(frozen=True)
class Palette:
    """Complete color palette for one simulation."""

    air: tuple[int, int, int]
    soil: tuple[int, int, int]
    sand: tuple[int, int, int]
    water: tuple[int, int, int]
    rock: tuple[int, int, int]

    # Future organisms will use these.
    plant_dark: tuple[int, int, int]
    plant: tuple[int, int, int]
    plant_light: tuple[int, int, int]

    insect: tuple[int, int, int]

    # Lighting colors.
    night_tint: tuple[int, int, int]
    dawn_tint: tuple[int, int, int]


class PaletteGenerator:
    """Creates visually coherent palettes."""

    def __init__(self, randomizer: Randomizer) -> None:
        self.randomizer = randomizer

    def generate(self) -> Palette:
        """
        Generate a new palette.

        The palette changes between runs, but all colors remain
        related to one another.
        """
        base_hue = self.randomizer.uniform(
            0.08,
            0.22,
        )

        # A small secondary hue variation gives the palette
        # some natural color diversity.
        green_hue = (
            base_hue
            + self.randomizer.uniform(
                0.02,
                0.08,
            )
        ) % 1.0

        water_hue = (
            base_hue
            + self.randomizer.uniform(
                0.40,
                0.55,
            )
        ) % 1.0

        rock_hue = (
            base_hue
            + self.randomizer.uniform(
                -0.03,
                0.03,
            )
        ) % 1.0

        air_hue = (
            base_hue
            + self.randomizer.uniform(
                0.02,
                0.08,
            )
        ) % 1.0

        return Palette(
            air=_hsv_to_rgb(
                air_hue,
                0.16,
                self.randomizer.uniform(
                    0.10,
                    0.15,
                ),
            ),

            soil=_hsv_to_rgb(
                base_hue,
                self.randomizer.uniform(
                    0.38,
                    0.52,
                ),
                self.randomizer.uniform(
                    0.28,
                    0.38,
                ),
            ),

            sand=_hsv_to_rgb(
                base_hue,
                self.randomizer.uniform(
                    0.28,
                    0.43,
                ),
                self.randomizer.uniform(
                    0.62,
                    0.76,
                ),
            ),

            water=_hsv_to_rgb(
                water_hue,
                self.randomizer.uniform(
                    0.42,
                    0.62,
                ),
                self.randomizer.uniform(
                    0.48,
                    0.65,
                ),
            ),

            rock=_hsv_to_rgb(
                rock_hue,
                self.randomizer.uniform(
                    0.08,
                    0.20,
                ),
                self.randomizer.uniform(
                    0.34,
                    0.48,
                ),
            ),

            plant_dark=_hsv_to_rgb(
                green_hue,
                self.randomizer.uniform(
                    0.48,
                    0.68,
                ),
                self.randomizer.uniform(
                    0.20,
                    0.30,
                ),
            ),

            plant=_hsv_to_rgb(
                green_hue,
                self.randomizer.uniform(
                    0.50,
                    0.72,
                ),
                self.randomizer.uniform(
                    0.38,
                    0.52,
                ),
            ),

            plant_light=_hsv_to_rgb(
                green_hue,
                self.randomizer.uniform(
                    0.38,
                    0.60,
                ),
                self.randomizer.uniform(
                    0.60,
                    0.76,
                ),
            ),

            insect=_hsv_to_rgb(
                self.randomizer.uniform(
                    0.02,
                    0.12,
                ),
                self.randomizer.uniform(
                    0.40,
                    0.70,
                ),
                self.randomizer.uniform(
                    0.25,
                    0.45,
                ),
            ),

            night_tint=(
                self.randomizer.randint(15, 30),
                self.randomizer.randint(20, 35),
                self.randomizer.randint(35, 55),
            ),

            dawn_tint=(
                self.randomizer.randint(70, 100),
                self.randomizer.randint(45, 75),
                self.randomizer.randint(35, 65),
            ),
        )