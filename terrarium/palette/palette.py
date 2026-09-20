"""The colour roles used by the whole game.  Nothing else hard-codes a colour."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Palette:
    name: str
    # --- terrain ----------------------------------------------------------
    sand: tuple
    sand_dark: tuple
    soil: tuple
    soil_dark: tuple
    detritus: tuple
    detritus_dark: tuple
    rock: tuple
    rock_light: tuple
    water: tuple
    water_deep: tuple
    foam: tuple
    glass: tuple
    glass_edge: tuple
    cave: tuple
    # --- sky: (top, bottom) gradients ------------------------------------
    sky_night: tuple
    sky_dawn: tuple
    sky_day: tuple
    sky_dusk: tuple
    sun: tuple
    moon: tuple
    star: tuple
    # --- light tint multipliers (r, g, b floats) --------------------------
    light_night: tuple
    light_dawn: tuple
    light_day: tuple
    light_dusk: tuple
    # --- flora ------------------------------------------------------------
    greens: tuple           # dark -> light
    wood: tuple
    cactus: tuple
    dead_leaf: tuple
    rot: tuple
    petals: tuple
    flower_centers: tuple
    mushroom_caps: tuple
    mushroom_stalk: tuple
    seed: tuple
    # --- fauna --------------------------------------------------------------
    ant: tuple
    beetle_shells: tuple
    butterfly_wings: tuple
    firefly_body: tuple
    firefly_glow: tuple
    # --- ui ---------------------------------------------------------------
    ui_text: tuple
    ui_panel: tuple
    ui_accent: tuple
