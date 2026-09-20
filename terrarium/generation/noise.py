"""Tiny noise / filter helpers for world generation (numpy only)."""
from __future__ import annotations

import numpy as np


def smooth_noise_1d(rng_np, n: int, scale: float, octaves: int = 3, persistence: float = 0.5) -> np.ndarray:
    """Fractal value noise along one axis, normalised to 0..1."""
    x = np.arange(n, dtype=np.float32)
    total = np.zeros(n, np.float32)
    amp, norm = 1.0, 0.0
    for o in range(octaves):
        step = max(2.0, scale / (2 ** o))
        pts = int(n / step) + 3
        vals = rng_np.random(pts).astype(np.float32)
        t = x / step
        i = t.astype(np.int32)
        f = t - i
        f = f * f * (3 - 2 * f)
        total += amp * (vals[i] * (1 - f) + vals[i + 1] * f)
        norm += amp
        amp *= persistence
    return total / norm


def _blur_axis0(a: np.ndarray, r: int) -> np.ndarray:
    n = a.shape[0]
    padded = np.pad(a, [(r, r)] + [(0, 0)] * (a.ndim - 1), mode="edge")
    c = np.concatenate([np.zeros((1,) + a.shape[1:], a.dtype), np.cumsum(padded, axis=0)], axis=0)
    return (c[2 * r + 1:2 * r + 1 + n] - c[:n]) / (2 * r + 1)


def box_blur(a: np.ndarray, r: int) -> np.ndarray:
    """Separable box blur with radius ``r``."""
    a = a.astype(np.float32)
    if r <= 0:
        return a
    return _blur_axis0(_blur_axis0(a, r).T, r).T
