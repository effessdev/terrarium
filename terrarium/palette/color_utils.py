"""Small colour toolbox (no dependencies beyond the standard library)."""
from __future__ import annotations

import colorsys

RGB = tuple  # (r, g, b) ints 0-255


def clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return lo if v < lo else hi if v > hi else v


def hsv(h: float, s: float, v: float) -> RGB:
    """Hue in degrees, saturation/value 0-1 -> 8-bit RGB."""
    r, g, b = colorsys.hsv_to_rgb((h % 360.0) / 360.0, clamp(s), clamp(v))
    return (int(r * 255 + 0.5), int(g * 255 + 0.5), int(b * 255 + 0.5))


def to_hsv(c: RGB):
    h, s, v = colorsys.rgb_to_hsv(c[0] / 255.0, c[1] / 255.0, c[2] / 255.0)
    return h * 360.0, s, v


def lerp(a, b, t: float) -> RGB:
    t = clamp(t)
    return (int(a[0] + (b[0] - a[0]) * t + 0.5),
            int(a[1] + (b[1] - a[1]) * t + 0.5),
            int(a[2] + (b[2] - a[2]) * t + 0.5))


def scale(c, f: float) -> RGB:
    return (int(clamp(c[0] * f, 0, 255)), int(clamp(c[1] * f, 0, 255)), int(clamp(c[2] * f, 0, 255)))


def modulate(c, m) -> RGB:
    """Multiply a colour by a per-channel float triple (used for daylight tinting)."""
    return (int(clamp(c[0] * m[0], 0, 255)), int(clamp(c[1] * m[1], 0, 255)), int(clamp(c[2] * m[2], 0, 255)))


def jitter(c: RGB, rng, dh: float = 4.0, ds: float = 0.05, dv: float = 0.05) -> RGB:
    """Return a slightly different colour (used for per-plant variation)."""
    h, s, v = to_hsv(c)
    return hsv(h + rng.uniform(-dh, dh), s + rng.uniform(-ds, ds), v + rng.uniform(-dv, dv))


def _lin(c: float) -> float:
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def oklab(c: RGB):
    r, g, b = _lin(c[0]), _lin(c[1]), _lin(c[2])
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def distance(a: RGB, b: RGB) -> float:
    """Perceptual distance (OKLab, x100).  ~2 is barely noticeable, >15 is clearly different."""
    la, lb = oklab(a), oklab(b)
    return 100.0 * sum((x - y) ** 2 for x, y in zip(la, lb)) ** 0.5
