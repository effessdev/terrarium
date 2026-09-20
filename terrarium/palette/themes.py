"""Hand-tuned base themes.

A theme is only a handful of *anchor hues* (degrees).  ``generator.py`` derives every
colour role from them with fixed lightness/saturation ladders, which is what keeps every
run harmonious while still looking different.  Add a theme by appending to ``THEMES``.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    name: str
    sand_hue: float
    soil_hue: float
    leaf_hue: float
    sky_hue: float
    water_hue: float
    flower_hues: tuple
    glow_hue: float        # hue of dawn/dusk sky glow
    night_hue: float
    sat: float = 1.0       # global saturation multiplier
    val: float = 1.0       # global brightness multiplier


THEMES = (
    Theme("Sunny meadow",   sand_hue=42, soil_hue=22,  leaf_hue=108, sky_hue=205, water_hue=196,
          flower_hues=(345, 48, 280, 14), glow_hue=22, night_hue=235),
    Theme("Twilight lagoon", sand_hue=30, soil_hue=350, leaf_hue=150, sky_hue=222, water_hue=178,
          flower_hues=(315, 195, 45, 265), glow_hue=335, night_hue=255, sat=0.95),
    Theme("Autumn dune",    sand_hue=34, soil_hue=14,  leaf_hue=78,  sky_hue=200, water_hue=205,
          flower_hues=(8, 38, 330, 55), glow_hue=15, night_hue=240, sat=1.05),
    Theme("Mint oasis",     sand_hue=52, soil_hue=30,  leaf_hue=128, sky_hue=190, water_hue=185,
          flower_hues=(350, 300, 40, 12), glow_hue=30, night_hue=230, val=1.03),
    Theme("Rose desert",    sand_hue=18, soil_hue=8,   leaf_hue=122, sky_hue=212, water_hue=190,
          flower_hues=(330, 50, 285, 20), glow_hue=350, night_hue=250, sat=0.92),
    Theme("Jade garden",    sand_hue=46, soil_hue=28,  leaf_hue=140, sky_hue=208, water_hue=170,
          flower_hues=(355, 42, 265, 320), glow_hue=25, night_hue=232),
)
