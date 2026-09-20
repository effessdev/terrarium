"""The world grid: a stack of numpy layers describing every cell.

Layers (all shaped ``(height, width)``; index as ``layer[y, x]``):
    mat        uint8   terrain material (see ``materials.Mat``)
    wet        uint8   moisture 0-255 (only meaningful for porous materials)
    tint       uint8   per-grain colour variation, travels with the grain
    flora      uint8   plant part code (0 = none, see ``flora.parts.Part``)
    flora_id   int32   id of the owning plant (0 = none)
    flora_rgb  uint8   (h, w, 3) final colour of the plant cell

Rows grow downwards: y = 0 is the lid of the terrarium.
Scalar accessors use ``ndarray.item`` which is ~3x faster than ``arr[y, x]``.
"""
from __future__ import annotations

import numpy as np

from .materials import AIR, GLASS, SOLID_PY, WATER


class Grid:
    def __init__(self, width: int, height: int) -> None:
        self.w = width
        self.h = height
        shape = (height, width)
        self.mat = np.zeros(shape, np.uint8)
        self.wet = np.zeros(shape, np.uint8)
        self.tint = np.zeros(shape, np.uint8)
        self.flora = np.zeros(shape, np.uint8)
        self.flora_id = np.zeros(shape, np.int32)
        self.flora_rgb = np.zeros((height, width, 3), np.uint8)
        self.build_border()

    # -- construction -------------------------------------------------
    def build_border(self) -> None:
        m = self.mat
        m[0, :] = GLASS
        m[-1, :] = GLASS
        m[:, 0] = GLASS
        m[:, -1] = GLASS

    # -- scalar queries -----------------------------------------------
    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.w and 0 <= y < self.h

    def mat_at(self, x: int, y: int) -> int:
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.mat.item(y, x)
        return GLASS

    def is_solid(self, x: int, y: int) -> bool:
        return SOLID_PY[self.mat_at(x, y)]

    def is_air(self, x: int, y: int) -> bool:
        return 0 <= x < self.w and 0 <= y < self.h and self.mat.item(y, x) == AIR

    def is_water(self, x: int, y: int) -> bool:
        return self.mat_at(x, y) == WATER

    def set_cell(self, x: int, y: int, mat: int, wet: int = 0, tint: int = 128) -> None:
        self.mat[y, x] = mat
        self.wet[y, x] = wet
        self.tint[y, x] = tint

    def surface_y(self, x: int) -> int:
        """Row of the top-most non-air cell in column ``x`` (ignores plants)."""
        col = self.mat[1:, x] != AIR
        return int(np.argmax(col)) + 1

    def ground_anchor(self, x: int):
        """Row of the free cell sitting directly on solid ground in column ``x``.

        Returns ``None`` when the column's top is water, the lid or the floor."""
        if not 0 < x < self.w - 1:
            return None
        y = self.surface_y(x)
        if y <= 1 or y >= self.h - 1:
            return None
        if not SOLID_PY[self.mat.item(y, x)]:
            return None
        return y - 1
