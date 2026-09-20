"""The ``Plant`` entity: a life-cycle state machine that stamps itself into the grid.

Life cycle:   GROWING -> MATURE -> (old age / drought / eaten / uprooted) -> DEAD (rotting)
Rotting cells vanish gradually and may turn into DETRITUS, which later becomes soil
(see ``ecology/decomposition.py``), closing the nutrient loop.

Every living cell of a plant is written into three grid layers (``flora``, ``flora_id``,
``flora_rgb``), so rendering and insect queries are plain vectorised numpy lookups.
"""
from __future__ import annotations

import numpy as np

from ..world.materials import AIR, DETRITUS, POROUS, SOLID_PY
from .growth import blueprint_step  # noqa: F401  (re-exported for species modules)

GROWING, MATURE, DEAD = 0, 1, 2


def _mix(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)


class Plant:
    def __init__(self, uid, species, x, y, colors, lifespan, palette, rng) -> None:
        self.id = uid
        self.species = species
        self.x = x                    # anchor cell: the free cell on top of the ground
        self.y = y
        self.cells: dict = {}         # (x, y) -> (part, shade)
        self.colors = colors
        self.palette = palette
        self.state = GROWING
        self.age = 0.0
        self.lifespan = lifespan
        self.steps = 0
        self.max_steps = species.max_steps
        self.growth = 0.0
        self.fail = 0
        self.hydration = 0.75
        self.dry_time = 0.0
        self.health = 1.0
        self.nectar = 1.0
        self.pollinated = False
        self.data: dict = {}
        self.removed = False
        self.wilt = 0.0
        self._wilt_drawn = 0.0
        self.decay = 0.0
        self.dead_age = 0.0
        self.rot_n0 = 1
        self.seed_timer = rng.uniform(*species.seed_interval)

    # ------------------------------------------------------------ cell access
    def color_of(self, part, shade, x, y):
        base = self.colors.get(part) or self.colors[0]
        n = ((x * 73856093) ^ (y * 19349663)) & 7
        f = (0.70 + 0.42 * shade) * (1.0 + (n - 3.5) * 0.012)
        c = (base[0] * f, base[1] * f, base[2] * f)
        if self.wilt > 0.0:
            c = _mix(c, self.palette.dead_leaf, self.wilt * 0.65)
        if self.decay > 0.0:
            c = _mix(c, self.palette.rot, self.decay)
        return (min(255, max(0, int(c[0]))), min(255, max(0, int(c[1]))), min(255, max(0, int(c[2]))))

    def add_cell(self, ctx, x, y, part, shade=0.5) -> bool:
        g = ctx.grid
        if not (0 < x < g.w - 1 and 0 < y < g.h - 1):
            return False
        if g.mat.item(y, x) != AIR:
            return False
        fid = g.flora_id.item(y, x)
        if fid and fid != self.id:
            return False
        self.cells[(x, y)] = (int(part), shade)
        g.flora[y, x] = int(part)
        g.flora_id[y, x] = self.id
        g.flora_rgb[y, x] = self.color_of(int(part), shade, x, y)
        return True

    def remove_cell(self, ctx, x, y) -> None:
        if self.cells.pop((x, y), None) is None:
            return
        g = ctx.grid
        if g.flora_id.item(y, x) == self.id:
            g.flora[y, x] = 0
            g.flora_id[y, x] = 0

    def recolor(self, ctx) -> None:
        g = ctx.grid
        for (x, y), (part, shade) in self.cells.items():
            g.flora_rgb[y, x] = self.color_of(part, shade, x, y)
        self._wilt_drawn = self.wilt

    def shift(self, ctx, dy: int) -> None:
        """Move the whole plant vertically (ground settled / was buried)."""
        old = self.cells
        for (x, y) in old:
            self.remove_cell_raw(ctx, x, y)
        self.cells = {}
        self.y += dy
        for (x, y), (part, shade) in old.items():
            self.add_cell(ctx, x, y + dy, part, shade)

    def remove_cell_raw(self, ctx, x, y) -> None:
        g = ctx.grid
        if g.flora_id.item(y, x) == self.id:
            g.flora[y, x] = 0
            g.flora_id[y, x] = 0

    # ------------------------------------------------------------ life cycle
    def fast_forward(self, ctx, steps: int) -> None:
        sp = self.species
        for _ in range(steps):
            if self.steps >= self.max_steps:
                break
            if sp.grow(self, ctx):
                self.steps += 1
            else:
                break
        if self.steps >= self.max_steps:
            self._become_mature(ctx)

    def _become_mature(self, ctx) -> None:
        if self.state == GROWING:
            self.state = MATURE
            self.species.on_mature(self, ctx)

    def die(self, ctx, cause: str) -> None:
        if self.state == DEAD:
            return
        self.state = DEAD
        self.dead_age = 0.0
        self.rot_n0 = max(1, len(self.cells))
        self.decay = 0.35
        ctx.bus.emit("plant_died", plant=self, cause=cause)
        if self.cells:
            self.recolor(ctx)
        else:
            self.removed = True

    def eat_cell(self, ctx, x, y) -> None:
        """Called by herbivores: bites one cell off."""
        if (x, y) not in self.cells or self.state == DEAD:
            return
        sp = self.species
        sp.on_eaten(self, ctx, x, y)
        self.health -= sp.bite_damage
        if sp.regrows:
            self.steps = max(0, self.steps - 1)
            if self.state == MATURE:
                self.state = GROWING
        if not self.cells or self.health <= 0.0:
            self.die(ctx, "eaten")

    # ------------------------------------------------------------ per-update
    def update(self, ctx, dt: float) -> None:
        self.age += dt
        if self.state == DEAD:
            self._rot(ctx, dt)
            return
        if not self._validate(ctx):
            return
        sp = self.species
        self._hydrate(ctx, dt)
        if self.age >= self.lifespan:
            self.die(ctx, "old age")
            return
        if self.dry_time > sp.drought_tolerance:
            self.die(ctx, "drought")
            return
        if self.health < 1.0:
            self.health = min(1.0, self.health + 0.004 * dt)
        self.nectar = min(1.0, self.nectar + 0.03 * dt)
        if self.state == GROWING:
            self._grow(ctx, dt)
        else:
            self._reproduce(ctx, dt)
        if abs(self.wilt - self._wilt_drawn) > 0.2:
            self.recolor(ctx)

    def _validate(self, ctx) -> bool:
        g = ctx.grid
        for (x, y) in list(self.cells):
            if g.mat.item(y, x) != AIR:                 # buried by sand / flooded
                self.remove_cell(ctx, x, y)
        if not self.cells:
            self.die(ctx, "buried")
            return False
        sp = self.species
        if not sp.rooted:
            if not sp.support_ok(self, ctx):
                self.die(ctx, "no support")
                return False
            return True
        x, y = self.x, self.y
        if SOLID_PY[g.mat_at(x, y + 1)] and g.mat_at(x, y) == AIR:
            return True
        new_y = g.ground_anchor(x)                      # ground moved: try to re-root
        if new_y is None or abs(new_y - y) > 4:
            self.die(ctx, "uprooted")
            return False
        self.shift(ctx, new_y - y)
        if not self.cells:
            self.die(ctx, "uprooted")
            return False
        return True

    def _hydrate(self, ctx, dt: float) -> None:
        sp = self.species
        g = ctx.grid
        self.hydration = max(0.0, self.hydration - sp.water_use * dt)
        if self.hydration < 0.9:
            x0, x1 = max(1, self.x - sp.root_radius), min(g.w - 1, self.x + sp.root_radius + 1)
            y0 = self.y + 1
            y1 = min(g.h - 1, y0 + sp.root_depth)
            if y1 > y0:
                win = g.wet[y0:y1, x0:x1]
                avail = (win > 18) & POROUS[g.mat[y0:y1, x0:x1]]
                n = int(avail.sum())
                if n:
                    want = (0.95 - self.hydration) * sp.water_capacity
                    per = min(want / n, 6.0)
                    dec = np.floor(per + ctx.rng.np.random(win.shape)).astype(np.int16) * avail
                    dec = np.minimum(dec, win)
                    taken = int(dec.sum())
                    if taken:
                        win -= dec.astype(np.uint8)
                        self.hydration = min(1.0, self.hydration + taken / sp.water_capacity)
                        top = min(self.cells, key=lambda c: c[1])[1] if self.cells else self.y
                        ctx.vapor.add(self.x, top, 0.5 * taken / ctx.config.physics.water_to_wet)
        if self.hydration <= 0.02:
            self.dry_time += dt
        else:
            self.dry_time = max(0.0, self.dry_time - dt)
        self.wilt = max(0.0, min(1.0, (0.35 - self.hydration) / 0.35))

    def _grow(self, ctx, dt: float) -> None:
        sp = self.species
        self.growth += sp.growth_rate * sp.env_factor(self, ctx) * dt
        while self.growth >= 1.0:
            self.growth -= 1.0
            if sp.grow(self, ctx):
                self.steps += 1
                self.fail = 0
            else:
                self.fail += 1
                if self.fail >= 3:
                    self.steps = self.max_steps
            if self.steps >= self.max_steps:
                self._become_mature(ctx)
                break

    def _reproduce(self, ctx, dt: float) -> None:
        self.seed_timer -= dt
        if self.seed_timer > 0.0:
            return
        sp = self.species
        rng = ctx.rng
        self.seed_timer = rng.uniform(*sp.seed_interval)
        if self.hydration < 0.35 or not self.cells or not sp.can_seed(self, ctx):
            return
        if sp.needs_pollination and not self.pollinated and not rng.chance(sp.self_seed_chance):
            return
        if ctx.flora.count(sp.name) >= sp.max_population:
            return
        ox, oy = sp.seed_origin(self)
        for _ in range(rng.randint(*sp.seeds_per_event)):
            ctx.seeds.launch(sp, ox, oy)
        self.pollinated = False

    def _rot(self, ctx, dt: float) -> None:
        sp = self.species
        self.dead_age += dt
        prog = min(1.0, self.dead_age / sp.rot_time)
        new_decay = 0.35 + 0.65 * prog
        if new_decay - self.decay > 0.15:
            self.decay = new_decay
            self.recolor(ctx)
        left = int(self.rot_n0 * (1.0 - prog))
        excess = len(self.cells) - left
        if excess > 0:
            g = ctx.grid
            rng = ctx.rng
            victims = rng.py.sample(list(self.cells), min(excess, len(self.cells)))
            for (x, y) in victims:
                self.remove_cell(ctx, x, y)
                if rng.chance(sp.detritus_yield) and g.mat.item(y, x) == AIR:
                    g.set_cell(x, y, DETRITUS, wet=90, tint=rng.randint(60, 200))
        if not self.cells:
            self.removed = True
