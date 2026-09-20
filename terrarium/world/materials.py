"""Terrain materials and their physical property tables.

Each table is a numpy array indexed by material id, so vectorised code can do
``DENSITY[grid.mat]``.  To add a material: append to ``Mat``, extend *every* table below
(the assertion in ``_lut`` catches a forgotten one) and give it a colour in
``render/layers/terrain.py``.
"""
from __future__ import annotations

from enum import IntEnum

import numpy as np


class Mat(IntEnum):
    AIR = 0
    SAND = 1
    SOIL = 2
    DETRITUS = 3   # rotting organic matter
    WATER = 4
    ROCK = 5
    GLASS = 6      # terrarium walls


AIR, SAND, SOIL, DETRITUS, WATER, ROCK, GLASS = (int(m) for m in Mat)
N_MATERIALS = len(Mat)


def _lut(values, dtype):
    assert len(values) == N_MATERIALS, "material table is missing an entry"
    return np.array(values, dtype=dtype)


#                     AIR SAND SOIL DETR WATER ROCK GLASS
DENSITY   = _lut([0,  40,  40,  40,  20,  255, 255], np.uint8)     # heavier sinks
MOVABLE   = _lut([0,   1,   1,   1,   1,    0,   0], bool)         # obeys gravity
COHESION  = _lut([256, 150, 70,  110, 256, 256, 256], np.uint16)   # wetness that "glues" grains
SLIDE     = _lut([0,  .9,  .55, .5,  1.0,   0,   0], np.float32)   # chance to slide diagonally
POROUS    = _lut([0,   1,   1,   1,   0,    0,   0], bool)         # can hold moisture
SOLID     = _lut([0,   1,   1,   1,   0,    1,   1], bool)         # creatures can stand on it
SHADOWS   = _lut([0,   1,   1,   1,   0,    1,   0], bool)         # blocks sunlight (not glass)
DIGGABLE  = _lut([0,   1,   1,   0,   0,    0,   0], bool)         # insects may move it
FIELD_CAP = _lut([0,  60,  110, 130,  0,    0,   0], np.float32)   # moisture held without draining

SOLID_PY = tuple(bool(v) for v in SOLID)
DIGGABLE_PY = tuple(bool(v) for v in DIGGABLE)
COHESION_PY = tuple(int(v) for v in COHESION)
