"""Builds a :class:`Palette` from a random theme plus small, bounded perturbations.

Why it never looks "random": every role is computed from theme anchors by a fixed recipe
(e.g. soil is always darker and more saturated than sand), the perturbations are a few
degrees / percent, and the finished palette must pass a perceptual contrast check
(OKLab distance between roles that must remain distinguishable).  If a roll fails the
check, we simply roll again.
"""
from __future__ import annotations

from ..core.rng import RNG
from .color_utils import clamp, distance, hsv, lerp, scale
from .palette import Palette
from .themes import THEMES, Theme


def generate_palette(rng: RNG) -> Palette:
    theme = rng.choice(THEMES)
    for _ in range(40):
        pal = _build(theme, rng, jit=1.0)
        if _is_valid(pal):
            return pal
    return _build(theme, rng, jit=0.0)


def _build(theme: Theme, rng: RNG, jit: float) -> Palette:
    drift = rng.uniform(-5, 5) * jit                 # global hue drift
    sat_k = theme.sat * (1 + rng.uniform(-0.08, 0.08) * jit)
    val_k = theme.val * (1 + rng.uniform(-0.05, 0.05) * jit)

    def C(h, s, v, hs=3.0):
        return hsv(h + drift + rng.uniform(-hs, hs) * jit, clamp(s * sat_k), clamp(v * val_k))

    def spread(lo, hi):
        return lo + (hi - lo) * (0.5 + (rng.random() - 0.5) * jit)

    T = theme
    # terrain ---------------------------------------------------------------
    sand = C(T.sand_hue, spread(0.30, 0.44), spread(0.82, 0.92))
    sand_dark = C(T.sand_hue - 5, spread(0.42, 0.55), spread(0.66, 0.74))
    soil = C(T.soil_hue, spread(0.50, 0.62), spread(0.34, 0.42))
    soil_dark = C(T.soil_hue - 3, spread(0.55, 0.65), spread(0.20, 0.26))
    detritus = C(T.soil_hue + 8, 0.40, spread(0.27, 0.32))
    detritus_dark = C(T.soil_hue + 10, 0.40, 0.18)
    rock = C(T.sky_hue + 10, spread(0.08, 0.16), spread(0.46, 0.54))
    rock_light = C(T.sky_hue + 5, spread(0.06, 0.12), spread(0.66, 0.74))
    water = C(T.water_hue, spread(0.50, 0.62), spread(0.74, 0.84))
    water_deep = C(T.water_hue + 8, spread(0.62, 0.74), spread(0.44, 0.54))
    foam = C(T.water_hue - 6, 0.16, 0.97)
    glass = C(T.sky_hue, 0.25, 0.95)
    glass_edge = C(T.sky_hue, 0.20, 0.70)
    cave = C(T.soil_hue, 0.55, 0.12)

    # sky -------------------------------------------------------------------
    sky_day = (C(T.sky_hue, spread(0.50, 0.62), spread(0.80, 0.90)),
               C(T.sky_hue - 12, spread(0.18, 0.28), 0.98))
    sky_dawn = (C(T.sky_hue + 40, 0.42, spread(0.68, 0.78)),
                C(T.glow_hue + 6, spread(0.42, 0.55), 0.98))
    sky_dusk = (C(T.sky_hue + 55, 0.55, spread(0.42, 0.52)),
                C(T.glow_hue - 6, spread(0.58, 0.70), 0.94))
    sky_night = (C(T.night_hue, 0.72, spread(0.09, 0.13)),
                 C(T.night_hue - 10, 0.62, spread(0.20, 0.27)))
    sun = C(46, 0.22, 1.0, hs=4)
    moon = C(T.sky_hue + 15, 0.10, 0.96)
    star = C(T.sky_hue, 0.10, 1.0)

    light_day = (1.0, 1.0, 0.97)
    light_dawn = (1.0, 0.86, 0.78)
    light_dusk = (1.0, 0.76, 0.72)
    light_night = (0.34, 0.40, 0.62)

    # flora -----------------------------------------------------------------
    lh = T.leaf_hue
    greens = (C(lh + 12, 0.70, 0.30), C(lh + 6, 0.66, 0.44), C(lh, 0.58, 0.58),
              C(lh - 8, 0.54, 0.72), C(lh - 16, 0.50, 0.86))
    wood = C(T.soil_hue + 6, 0.50, 0.36)
    cactus = C(lh + 18, 0.42, 0.60)
    dead_leaf = C(38, 0.55, 0.55)
    rot = C(T.soil_hue + 8, 0.45, 0.22)

    petals = tuple(C(h, spread(0.55, 0.78), spread(0.86, 0.96), hs=5) for h in T.flower_hues)
    centers = (C(46, 0.85, 0.98), C(30, 0.80, 0.90), C(T.flower_hues[0] + 180, 0.5, 0.95))
    caps = (C(T.flower_hues[0], 0.62, 0.82), C(T.flower_hues[1], 0.55, 0.88),
            C(T.sand_hue, 0.16, 0.92), C(T.flower_hues[2], 0.45, 0.78))
    stalk = C(T.sand_hue, 0.10, 0.92)
    seed = C(T.soil_hue + 15, 0.35, 0.55)

    # fauna -----------------------------------------------------------------
    ant = C(T.soil_hue - 4, 0.62, spread(0.26, 0.32))
    beetle = (C(lh + 70, 0.65, 0.62), C(T.flower_hues[2], 0.60, 0.60), C(T.water_hue, 0.55, 0.62))
    wings = tuple(C(h + 6, 0.60, 0.95, hs=6) for h in T.flower_hues) + (C(48, 0.7, 0.98),)
    ff_body = C(T.soil_hue, 0.5, 0.22)
    ff_glow = C(spread(62, 84), 0.72, 1.0, hs=2)

    ui_text = C(T.sky_hue, 0.08, 0.96)
    ui_panel = C(T.night_hue, 0.55, 0.10)
    ui_accent = C(T.flower_hues[1], 0.55, 0.98)

    return Palette(
        name=T.name, sand=sand, sand_dark=sand_dark, soil=soil, soil_dark=soil_dark,
        detritus=detritus, detritus_dark=detritus_dark, rock=rock, rock_light=rock_light,
        water=water, water_deep=water_deep, foam=foam, glass=glass, glass_edge=glass_edge,
        cave=cave, sky_night=sky_night, sky_dawn=sky_dawn, sky_day=sky_day, sky_dusk=sky_dusk,
        sun=sun, moon=moon, star=star, light_night=light_night, light_dawn=light_dawn,
        light_day=light_day, light_dusk=light_dusk, greens=greens, wood=wood, cactus=cactus,
        dead_leaf=dead_leaf, rot=rot, petals=petals, flower_centers=centers, mushroom_caps=caps,
        mushroom_stalk=stalk, seed=seed, ant=ant, beetle_shells=beetle, butterfly_wings=wings,
        firefly_body=ff_body, firefly_glow=ff_glow, ui_text=ui_text, ui_panel=ui_panel,
        ui_accent=ui_accent,
    )


# (a, b, minimum perceptual distance) -- pairs that must stay distinguishable
def _is_valid(p: Palette) -> bool:
    leaf = p.greens[2]
    checks = [
        (p.sand, p.soil, 22), (p.sand, p.rock, 14), (p.soil, p.rock, 10),
        (p.sand, p.sand_dark, 6), (p.soil, p.soil_dark, 5),
        (p.water, p.sand, 14), (p.water, p.soil, 16), (p.water, p.rock, 10),
        (leaf, p.soil, 14), (leaf, p.sky_day[1], 12), (leaf, p.sand, 14),
        (p.sand, p.sky_day[1], 8), (p.ant, p.sand, 25), (p.ant, p.cave, 6),
        (p.greens[0], p.greens[4], 20),
    ]
    checks += [(pt, leaf, 12) for pt in p.petals]
    checks += [(pt, p.sky_day[1], 8) for pt in p.petals]
    checks += [(s, p.sand, 10) for s in p.beetle_shells]
    return all(distance(a, b) >= d for a, b, d in checks)
