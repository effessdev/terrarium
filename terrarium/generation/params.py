"""Per-run world parameters: the dice that make every terrarium different."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WorldParams:
    ground_level: float      # fraction of the height where the ground sits
    roughness: float         # amplitude of hills
    n_dunes: int
    aridity: float           # 0 = lush / wet, 1 = dry desert
    n_ponds: int
    pond_width: tuple
    n_rocks: int
    n_buried_rocks: int
    warmth_bias: float       # shifts the climate a little warmer / cooler
    start_phase: float       # time of day when the run starts
    plant_mix: dict          # species name -> multiplier on initial abundance
    describe: str = ""


def roll_params(rng) -> WorldParams:
    aridity = rng.random() ** 1.3
    lush = 1.0 - aridity
    return WorldParams(
        ground_level=rng.uniform(0.48, 0.60),
        roughness=rng.uniform(0.35, 1.0),
        n_dunes=rng.randint(1, 4),
        aridity=aridity,
        n_ponds=rng.choice((1, 1, 2, 2, 3)) if aridity < 0.75 else rng.choice((0, 1, 1)),
        pond_width=(rng.randint(8, 13), rng.randint(14, 26)),
        n_rocks=rng.randint(3, 9),
        n_buried_rocks=rng.randint(1, 4),
        warmth_bias=rng.uniform(-0.04, 0.06) + 0.05 * aridity,
        start_phase=rng.uniform(0.2, 0.55),
        plant_mix={
            "grass": rng.uniform(0.5, 1.5) * (0.4 + lush),
            "fern": rng.uniform(0.3, 1.6) * lush * 1.4,
            "flower": rng.uniform(0.5, 1.6),
            "moss": rng.uniform(0.4, 1.5) * (0.3 + lush),
            "mushroom": rng.uniform(0.3, 1.4) * lush,
            "bush": rng.uniform(0.3, 1.4),
            "cactus": rng.uniform(0.3, 1.5) * (0.2 + 2.2 * aridity),
        },
        describe="arid" if aridity > 0.6 else "lush" if aridity < 0.3 else "temperate",
    )
