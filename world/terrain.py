"""Terrain data structures."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TerrainType(Enum):
    """Types of terrain currently supported by the simulation."""

    AIR = 0
    SOIL = 1
    SAND = 2
    WATER = 3
    ROCK = 4


@dataclass
class TerrainCell:
    """A single cell in the terrarium terrain grid."""

    terrain_type: TerrainType = TerrainType.AIR

    # These values will become important in later phases.
    moisture: float = 0.0
    nutrients: float = 0.0

    def is_solid(self) -> bool:
        """Return whether this cell is solid ground."""
        return self.terrain_type in {
            TerrainType.SOIL,
            TerrainType.SAND,
            TerrainType.ROCK,
        }

    def is_water(self) -> bool:
        """Return whether this cell contains water."""
        return self.terrain_type == TerrainType.WATER
