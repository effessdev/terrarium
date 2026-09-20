"""FloraSystem: owns every plant, spreads their updates over time, tracks populations."""
from __future__ import annotations

from collections import defaultdict

from ..core.system import System
from ..world.materials import AIR
from .plant import DEAD, MATURE, Plant
from .registry import all_species


class FloraSystem(System):
    name = "flora"
    interval = 1

    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        self.plants: list[Plant] = []
        self.by_id: dict[int, Plant] = {}
        self._counts: dict[str, int] = defaultdict(int)
        self._next_id = 1
        self._dirty = False
        ctx.bus.subscribe("plant_died", self._on_died)
        ctx.bus.subscribe("dawn", lambda: self._phase(True))
        ctx.bus.subscribe("dusk", lambda: self._phase(False))

    # ------------------------------------------------------------ queries
    def count(self, name: str) -> int:
        return self._counts[name]

    def total(self) -> int:
        return sum(self._counts.values())

    def get(self, pid: int):
        return self.by_id.get(pid)

    # ------------------------------------------------------------ creation
    def spawn(self, species, x: int, y: int, steps: int = 0, age_frac: float = 0.0):
        ctx = self.ctx
        g = ctx.grid
        if len(self.plants) >= ctx.config.flora.max_plants:
            return None
        if not (0 < x < g.w - 1 and 0 < y < g.h - 1):
            return None
        if g.mat.item(y, x) != AIR or g.flora_id.item(y, x):
            return None
        rng = ctx.rng
        plant = Plant(self._next_id, species, x, y, species.make_colors(ctx.palette, rng),
                      rng.uniform(*species.lifespan), ctx.palette, rng)
        self._next_id += 1
        species.on_create(plant, ctx)
        if not plant.cells and species.grow(plant, ctx):
            plant.steps = 1
        if not plant.cells:
            return None
        if steps:
            plant.fast_forward(ctx, steps)
        plant.age = plant.lifespan * age_frac
        self.plants.append(plant)
        self.by_id[plant.id] = plant
        self._counts[species.name] += 1
        return plant

    def find_spot(self, species, tries: int = 80):
        """Random anchor cell where ``species`` could live right now, or None."""
        g = self.ctx.grid
        rng = self.ctx.rng
        sp = species.spacing
        for _ in range(tries):
            x = rng.randint(3, g.w - 4)
            y = g.ground_anchor(x)
            if y is None or y < 6:
                continue
            if not rng.chance(species.suitability(self.ctx, x, y)):
                continue
            if g.flora_id[max(0, y - 3):y + 1, max(0, x - sp):x + sp + 1].any():
                continue
            return x, y
        return None

    def germinate_random(self, species, n: int = 1) -> int:
        made = 0
        for _ in range(n):
            spot = self.find_spot(species)
            if spot and self.spawn(species, *spot):
                made += 1
        return made

    # ------------------------------------------------------------ simulation
    def update(self, dt: float) -> None:
        step = self.ctx.config.flora.update_interval
        dt_eff = step * self.ctx.config.tick_dt
        plants = self.plants
        for i in range(self.ctx.tick % step, len(plants), step):
            p = plants[i]
            if not p.removed:
                p.update(self.ctx, dt_eff)
                if p.removed:
                    self._dirty = True
        if self._dirty:
            for p in plants:
                if p.removed:
                    self.by_id.pop(p.id, None)
            self.plants = [p for p in plants if not p.removed]
            self._dirty = False

    # ------------------------------------------------------------ events
    def _on_died(self, plant, cause) -> None:
        self._counts[plant.species.name] -= 1

    def _phase(self, is_day: bool) -> None:
        ctx = self.ctx
        for p in self.plants:
            if p.state != DEAD and p.species.reacts_to_phase:
                p.species.on_phase(p, ctx, is_day)

    def living(self):
        return (p for p in self.plants if p.state != DEAD)
