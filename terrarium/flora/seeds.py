"""Seeds / spores: tiny particles that drift, land, wait for moisture and germinate."""
from __future__ import annotations

from ..core.system import System
from ..world.materials import AIR, WATER


class Seed:
    __slots__ = ("x", "y", "vx", "vy", "species", "landed", "age")

    def __init__(self, x, y, vx, vy, species) -> None:
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.species = species
        self.landed = False
        self.age = 0.0


class SeedSystem(System):
    name = "seeds"
    interval = 1

    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        self.airborne: list[Seed] = []
        self.landed: list[Seed] = []

    def launch(self, species, x, y) -> None:
        cfg = self.ctx.config.flora
        if len(self.airborne) + len(self.landed) >= cfg.max_seeds:
            return
        rng = self.ctx.rng
        sp = rng.uniform(*species.seed_speed)
        self.airborne.append(Seed(x + 0.5, y + 0.5, rng.uniform(-1, 1) * sp, -rng.uniform(0.0, 0.8) * sp, species))

    def count(self) -> int:
        return len(self.airborne) + len(self.landed)

    # ------------------------------------------------------------------
    def update(self, dt: float) -> None:
        ctx = self.ctx
        g = ctx.grid
        rng = ctx.rng
        keep = []
        for s in self.airborne:
            s.vy = min(s.vy + 14.0 * dt, 7.0)
            s.vx += (rng.random() - 0.5) * 9.0 * dt
            s.vx *= 1.0 - 0.6 * dt
            nx = s.x + s.vx * dt
            if g.is_air(int(nx), int(s.y)):
                s.x = nx
            else:
                s.vx = 0.0
            ny = s.y + s.vy * dt
            m = g.mat_at(int(s.x), int(ny))
            if m == AIR:
                s.y = ny
                keep.append(s)
            elif m == WATER:
                continue                                   # drowned
            else:
                s.landed = True
                s.age = 0.0
                self.landed.append(s)
        self.airborne = keep
        if ctx.tick % 30 == 0:
            self._germination_pass()

    def _germination_pass(self) -> None:
        ctx = self.ctx
        g = ctx.grid
        rng = ctx.rng
        lifetime = ctx.config.flora.seed_lifetime
        keep = []
        for s in self.landed:
            s.age += 1.0
            x, y = int(s.x), int(s.y)
            sp = s.species
            if s.age > lifetime or not g.is_air(x, y):
                continue
            if not g.is_solid(x, y + 1):
                # ground vanished under it: let it fall again
                s.landed = False
                self.airborne.append(s)
                continue
            suit = sp.suitability(ctx, x, y)
            if suit > 0.0 and rng.chance(0.35 * suit) and ctx.flora.count(sp.name) < sp.max_population:
                if ctx.flora.spawn(sp, x, y) is not None:
                    continue
            keep.append(s)
        self.landed = keep

    # ------------------------------------------------------------------
    def nearest_landed(self, x: int, y: int, radius: int):
        best, bd = None, radius * radius + 1
        for s in self.landed:
            d = (s.x - x) ** 2 + (s.y - y) ** 2
            if d < bd:
                best, bd = s, d
        return best

    def remove(self, seed: Seed) -> None:
        try:
            self.landed.remove(seed)
        except ValueError:
            pass
