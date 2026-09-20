"""FaunaSystem: owns every insect, spatial hash for mate lookup, population counts."""
from __future__ import annotations

from collections import defaultdict

from ..core.system import System
from ..world.materials import AIR
from .behaviors.locomotion import support_level
from .insect import Insect


class FaunaSystem(System):
    name = "fauna"
    interval = 1

    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        self.insects: list[Insect] = []
        self._counts: dict[str, int] = defaultdict(int)
        self._next_id = 1
        self._buckets: dict = {}
        ctx.bus.subscribe("insect_died", self._on_died)

    # ------------------------------------------------------------ queries
    def count(self, name: str) -> int:
        return self._counts[name]

    def total(self) -> int:
        return sum(self._counts.values())

    def find_mate(self, ins, radius: int):
        bs = self.ctx.config.fauna.bucket_size
        bx, by = int(ins.x) // bs, int(ins.y) // bs
        best, bd = None, radius * radius + 1
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1):
                for o in self._buckets.get((bx + ox, by + oy), ()):
                    if o is ins or o.species is not ins.species or not o.can_breed():
                        continue
                    d = (o.x - ins.x) ** 2 + (o.y - ins.y) ** 2
                    if d < bd:
                        best, bd = o, d
        return best

    # ------------------------------------------------------------ creation
    def spot_ok(self, species, x: int, y: int) -> bool:
        g = self.ctx.grid
        if not g.is_air(x, y):
            return False
        return species.locomotion == "fly" or support_level(g, x, y) > 0

    def spawn(self, species, x: int, y: int, juvenile: bool = False):
        ctx = self.ctx
        cfg = ctx.config.fauna
        if len(self.insects) >= cfg.max_insects or self._counts[species.name] >= species.max_population + 6:
            return None
        rng = ctx.rng
        spot = None
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, -1), (1, -1), (-1, -1), (0, 1), (2, 0), (-2, 0), (0, -2)):
            if self.spot_ok(species, x + dx, y + dy):
                spot = (x + dx, y + dy)
                break
        if spot is None:
            return None
        px, py = spot
        if species.locomotion == "fly":
            px, py = px + 0.5, py + 0.5
        ins = Insect(self._next_id, species, px, py, species.make_colors(ctx.palette, rng),
                     rng.uniform(*species.lifespan), rng)
        self._next_id += 1
        if juvenile:
            ins.age = 0.0
            ins.energy = species.max_energy * 0.5
        else:
            ins.age = species.mature_age + rng.uniform(0.0, 0.3) * species.lifespan[0]
        self.insects.append(ins)
        self._counts[species.name] += 1
        return ins

    def find_spot(self, species, tries: int = 80):
        g = self.ctx.grid
        rng = self.ctx.rng
        for _ in range(tries):
            x = rng.randint(3, g.w - 4)
            gy = g.ground_anchor(x)
            if gy is None:
                continue
            y = gy if species.locomotion == "crawl" else max(4, gy - rng.randint(2, 30))
            if self.spot_ok(species, x, y):
                return x, y
        return None

    # ------------------------------------------------------------ simulation
    def update(self, dt: float) -> None:
        ctx = self.ctx
        if ctx.tick % 3 == 0:
            bs = ctx.config.fauna.bucket_size
            buckets: dict = defaultdict(list)
            for i in self.insects:
                buckets[(int(i.x) // bs, int(i.y) // bs)].append(i)
            self._buckets = buckets
        for i in self.insects:
            if i.alive:
                i.update(ctx, dt)
        if any(not i.alive for i in self.insects):
            self.insects = [i for i in self.insects if i.alive]

    def _on_died(self, insect, cause) -> None:
        self._counts[insect.species.name] -= 1
        self.ctx.corpses.add(int(insect.x), int(insect.y), insect.colors["body"])
