"""Coarse water-vapour field (one value per 4x4 block of cells).

Units: one evaporated water cell adds 1.0.  Warmer air holds more (``saturation``); the
top rows (next to the "cold glass lid") hold less, so vapour that rises condenses there.
"""
from __future__ import annotations

import numpy as np


class VaporField:
    BLOCK = 4
    LID_ROWS = 2                       # coarse rows that count as "cold glass"

    def __init__(self, grid_w: int, grid_h: int, capacity: float, diffusion: float, rise: float) -> None:
        b = self.BLOCK
        self.cw = (grid_w + b - 1) // b
        self.ch = (grid_h + b - 1) // b
        self.v = np.zeros((self.ch, self.cw), np.float32)
        self.capacity = capacity
        self.diffusion = diffusion
        self.rise = rise
        rows = np.arange(self.ch, dtype=np.float32) / max(1, self.ch - 1)
        self.row_factor = (0.45 + 0.55 * rows)[:, None]     # lower saturation near the lid

    # -- writes ----------------------------------------------------------
    def add(self, x: int, y: int, amount: float) -> None:
        b = self.BLOCK
        self.v[min(y // b, self.ch - 1), min(x // b, self.cw - 1)] += amount

    def add_many(self, xs, ys, amounts) -> None:
        b = self.BLOCK
        np.add.at(self.v, (np.minimum(ys // b, self.ch - 1), np.minimum(xs // b, self.cw - 1)), amounts)

    # -- reads -----------------------------------------------------------
    def saturation(self, temperature: float) -> np.ndarray:
        return self.capacity * (0.25 + 1.5 * temperature) * self.row_factor

    def humidity(self, temperature: float) -> np.ndarray:
        return self.v / self.saturation(temperature)

    def ratio_at(self, xs, ys, temperature: float):
        b = self.BLOCK
        by = np.minimum(ys // b, self.ch - 1)
        bx = np.minimum(xs // b, self.cw - 1)
        sat = self.capacity * (0.25 + 1.5 * temperature) * self.row_factor[by, 0]
        return self.v[by, bx] / sat

    # -- simulation --------------------------------------------------------
    def step(self, temperature: float, condensation_rate: float) -> np.ndarray:
        """Diffuse, lift and condense.  Returns vapour condensed on the lid per coarse column."""
        v = self.v
        p = np.pad(v, 1, mode="edge")
        nb = (p[:-2, 1:-1] + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]) * 0.25
        v += self.diffusion * (nb - v)
        lift = v[1:] * self.rise * (0.4 + temperature)
        v[:-1] += lift
        v[1:] -= lift
        excess = np.maximum(v - self.saturation(temperature), 0.0) * condensation_rate
        v -= excess
        lid = self.LID_ROWS
        condensed = excess[:lid].sum(axis=0)
        # over-saturated air deeper down is pushed one row up, so fog climbs to the lid
        v[lid - 1:-1] += excess[lid:]
        return condensed
