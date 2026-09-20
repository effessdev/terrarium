"""Plant part codes stored in ``grid.flora`` plus lookup tables built from them."""
from __future__ import annotations

from enum import IntEnum

import numpy as np


class Part(IntEnum):
    NONE = 0
    STEM = 1
    LEAF = 2
    PETAL = 3
    CENTER = 4
    MOSS = 5
    STALK = 6
    CAP = 7
    WOOD = 8
    CACTUS = 9
    BLADE = 10
    FROND = 11


def _mask(*parts) -> np.ndarray:
    lut = np.zeros(256, bool)
    for p in parts:
        lut[int(p)] = True
    return lut


#: parts herbivores may bite off
EDIBLE_LUT = _mask(Part.LEAF, Part.PETAL, Part.MOSS, Part.BLADE, Part.FROND, Part.CAP, Part.STALK)
#: parts that offer nectar to pollinators
NECTAR_LUT = _mask(Part.PETAL, Part.CENTER)
