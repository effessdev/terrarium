"""The ``Insect`` entity: shared state, metabolism, hazards and death."""
from __future__ import annotations

from ..world.materials import SOLID_PY, WATER
from .behaviors.locomotion import DIRS, fall_if_unsupported


class Insect:
    def __init__(self, uid, species, x, y, colors, lifespan, rng) -> None:
        self.id = uid
        self.species = species
        self.x = x
        self.y = y
        self.colors = colors
        self.lifespan = lifespan
        self.age = 0.0
        self.energy = species.max_energy * 0.7
        self.alive = True
        self.cooldown = species.repro_cooldown * rng.random()
        self.act_timer = rng.random()
        self.dir_idx = rng.randint(0, 7)
        self.heading = rng.uniform(0.0, 6.283)
        self.side = rng.sign()
        self.carry = None             # (material, wet, tint) while moving soil
        self.carry_time = 0
        self.target = None
        self.search_cd = rng.randint(0, 5)
        self.drown = 0.0
        self.buried = 0.0
        self.activity = 1.0
        self.perched = False
        self.behaviors = species.build_behaviors()

    # ------------------------------------------------------------------
    @property
    def juvenile(self) -> bool:
        return self.age < self.species.mature_age

    def can_breed(self) -> bool:
        sp = self.species
        return (self.alive and not self.juvenile and self.cooldown <= 0.0 and self.activity > 0.3
                and self.energy >= sp.repro_threshold * sp.max_energy)

    def die(self, ctx, cause: str) -> None:
        if not self.alive:
            return
        self.alive = False
        ctx.bus.emit("insect_died", insect=self, cause=cause)

    # ------------------------------------------------------------------
    def update(self, ctx, dt: float) -> None:
        sp = self.species
        self.age += dt
        self.cooldown -= dt
        act = sp.activity_level(ctx)
        self.activity = act
        self.energy -= sp.hunger_rate * dt * (0.35 + 0.65 * act)
        if self.energy <= 0.0:
            self.die(ctx, "starved")
            return
        if self.age >= self.lifespan:
            self.die(ctx, "old age")
            return
        if self._hazards(ctx, dt):
            return
        if sp.locomotion == "crawl":
            if fall_if_unsupported(self, ctx):
                return
            if act < 0.12:
                return                                    # asleep
            self.act_timer += dt * sp.speed * (0.25 + 0.75 * act) * (0.6 if self.juvenile else 1.0)
            n = 0
            while self.act_timer >= 1.0 and n < 4:
                self.act_timer -= 1.0
                n += 1
                for b in self.behaviors:
                    if b.update(self, ctx, 1.0 / max(sp.speed, 0.1)):
                        break
        else:
            for b in self.behaviors:
                if b.update(self, ctx, dt):
                    break

    # ------------------------------------------------------------------
    def _hazards(self, ctx, dt: float) -> bool:
        """Drowning and cave-ins.  Returns True if the insect was busy / died."""
        g = ctx.grid
        ix, iy = int(self.x), int(self.y)
        m = g.mat_at(ix, iy)
        if m == WATER:
            self.drown += dt
            if g.mat_at(ix, iy - 1) != WATER and not SOLID_PY[g.mat_at(ix, iy - 1)]:
                self.y = iy - 1
            elif self.drown > 3.0:
                self.die(ctx, "drowned")
                return True
            return False
        self.drown = max(0.0, self.drown - dt)
        if SOLID_PY[m]:                                  # sand fell onto us
            for dx, dy in DIRS:
                if g.is_air(ix + dx, iy + dy):
                    self.x, self.y = ix + dx, iy + dy
                    self.buried = 0.0
                    return True
            self.buried += dt
            if self.species.can_dig and self.buried > 1.0:
                g.set_cell(ix, iy, 0)
                self.buried = 0.0
            elif self.buried > 6.0:
                self.die(ctx, "crushed")
            return True
        self.buried = 0.0
        return False
