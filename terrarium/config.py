"""Central configuration.

Every tunable that is *global* (window, timing, climate, caps ...) lives here so that
nobody has to hunt through the code base for magic numbers.  Species-specific numbers
live next to the species they describe (see ``flora/species`` and ``fauna/species``).

All config objects are frozen dataclasses: create a modified copy with
``dataclasses.replace(cfg.window, cell_size=5)`` and pass it to ``Config``.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class WindowConfig:
    width: int = 1280
    height: int = 720
    #: Pixels per simulation cell.  4 -> 320x180 grid (recommended for iGPU / CPU-only).
    #: 5 -> 256x144 (faster), 2 -> 640x360 (prettier, ~4x slower).
    cell_size: int = 4
    fps_cap: int = 60
    title: str = "Terrarium"

    @property
    def grid_w(self) -> int:
        return self.width // self.cell_size

    @property
    def grid_h(self) -> int:
        return self.height // self.cell_size


@dataclass(frozen=True)
class TimeConfig:
    tick_rate: int = 30                 # simulation ticks per (simulated) second
    day_length: float = 120.0           # seconds of simulated time for a full day/night
    speeds: tuple = (0.0, 0.5, 1.0, 2.0, 4.0, 8.0)
    default_speed_index: int = 2
    max_ticks_per_frame: int = 8        # safety valve when the machine cannot keep up


@dataclass(frozen=True)
class PhysicsConfig:
    lateral_water_passes: int = 2       # how many sideways water-spreading passes per tick
    moisture_interval: int = 4          # ticks between moisture diffusion steps
    absorb_chance: float = 0.006         # chance a water cell soaks into porous ground
    water_to_wet: int = 200             # wetness units (0-255) that one water cell is worth
    drain_rate: float = 0.12
    diffusion_rate: float = 0.06


@dataclass(frozen=True)
class ClimateConfig:
    evap_interval: int = 6
    evaporation_water: float = 0.020    # per exposed water cell, per evaporation step
    evaporation_soil: float = 0.9       # wetness units lost by damp exposed soil per step
    vapor_capacity: float = 0.55        # vapor units one 4x4 cell block can hold at temp=0.5
    vapor_diffusion: float = 0.22
    vapor_rise: float = 0.05
    condensation_rate: float = 0.35
    drip_threshold: float = 1.0
    min_sunniness: float = 0.35


@dataclass(frozen=True)
class WorldGenConfig:
    settle_ticks: int = 90              # physics-only ticks used to settle terrain before start
    initial_plants: tuple = (110, 190)
    initial_insects: tuple = (34, 56)


@dataclass(frozen=True)
class FloraConfig:
    update_interval: int = 15           # every plant is updated once per N ticks
    max_plants: int = 650
    max_seeds: int = 260
    seed_lifetime: float = 140.0


@dataclass(frozen=True)
class FaunaConfig:
    max_insects: int = 240
    bucket_size: int = 10               # spatial hash bucket edge, in cells


@dataclass(frozen=True)
class EcologyConfig:
    rescue_enabled: bool = True         # dormant seeds / eggs revive vanished species
    rescue_delay: float = 100.0         # sim seconds a species must be extinct first
    detritus_half_life: float = 70.0    # seconds for rot to turn into fertile soil


@dataclass(frozen=True)
class RenderConfig:
    star_count: int = 140
    show_hud: bool = True
    fog_strength: float = 0.5


@dataclass(frozen=True)
class Config:
    window: WindowConfig = field(default_factory=WindowConfig)
    time: TimeConfig = field(default_factory=TimeConfig)
    physics: PhysicsConfig = field(default_factory=PhysicsConfig)
    climate: ClimateConfig = field(default_factory=ClimateConfig)
    worldgen: WorldGenConfig = field(default_factory=WorldGenConfig)
    flora: FloraConfig = field(default_factory=FloraConfig)
    fauna: FaunaConfig = field(default_factory=FaunaConfig)
    ecology: EcologyConfig = field(default_factory=EcologyConfig)
    render: RenderConfig = field(default_factory=RenderConfig)

    @property
    def tick_dt(self) -> float:
        return 1.0 / self.time.tick_rate
