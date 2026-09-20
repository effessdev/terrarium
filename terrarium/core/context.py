"""Shared state handed to every system: the single place where services live."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..config import Config
from ..palette.palette import Palette
from ..world.grid import Grid
from .events import EventBus
from .rng import RNG

if TYPE_CHECKING:  # pragma: no cover
    from ..climate.clock import DayClock
    from ..climate.weather import Weather
    from ..climate.vapor import VaporField
    from ..climate.water_cycle import WaterCycleSystem
    from ..ecology.corpses import CorpseSystem
    from ..ecology.director import EcologyDirector
    from ..fauna.system import FaunaSystem
    from ..flora.seeds import SeedSystem
    from ..flora.system import FloraSystem
    from ..generation.params import WorldParams


class SimContext:
    def __init__(self, config: Config, rng: RNG, palette: Palette) -> None:
        self.config = config
        self.rng = rng
        self.palette = palette
        self.bus = EventBus()
        self.grid = Grid(config.window.grid_w, config.window.grid_h)
        self.tick = 0
        self.time = 0.0                       # simulated seconds since start
        # services, attached by ``builder.build_simulation``
        self.params: "WorldParams" = None     # type: ignore[assignment]
        self.clock: "DayClock" = None         # type: ignore[assignment]
        self.weather: "Weather" = None        # type: ignore[assignment]
        self.vapor: "VaporField" = None       # type: ignore[assignment]
        self.water_cycle: "WaterCycleSystem" = None  # type: ignore[assignment]
        self.flora: "FloraSystem" = None      # type: ignore[assignment]
        self.seeds: "SeedSystem" = None       # type: ignore[assignment]
        self.fauna: "FaunaSystem" = None      # type: ignore[assignment]
        self.corpses: "CorpseSystem" = None   # type: ignore[assignment]
        self.ecology: "EcologyDirector" = None  # type: ignore[assignment]
        self.stats: dict[str, Any] = {}       # filled by the ecology director, read by the HUD

    @property
    def dt(self) -> float:
        return self.config.tick_dt
