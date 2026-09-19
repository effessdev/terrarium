"""Worm entity and its basic life cycle.

This simplified rewrite aims for robust, predictable behaviour while
maintaining the public API expected by the rest of the simulation.
Key changes:
- gentler hunger/dehydration accumulation
- starvation/dehydration only advances when near-critical
- clearer reproduction cooldowns
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math

from config import settings


class WormState(Enum):
    WANDERING = "wandering"
    SEEKING_FOOD = "seeking_food"
    SEEKING_WATER = "seeking_water"
    SLEEPING = "sleeping"
    DEAD = "dead"


@dataclass
class Worm:
    x: float
    y: float

    age: float = 0.0
    growth: float = 0.15

    hunger: float = 0.0
    thirst: float = 0.0

    state: WormState = WormState.WANDERING

    direction: float = 1.0

    wander_timer: float = 0.0
    reproduction_timer: float = 0.0

    starvation_time: float = 0.0
    dehydration_time: float = 0.0

    rot: float = 0.0

    target_x: float | None = None
    target_y: float | None = None

    def update_needs(self, dt: float) -> None:
        """Advance hunger and thirst with forgiving accumulation."""
        if self.is_dead:
            return

        self.age += dt

        # Base accumulation; tuned in settings. Clamp to [0,1].
        self.hunger = min(1.0, self.hunger + settings.WORM_HUNGER_RATE * dt)
        self.thirst = min(1.0, self.thirst + settings.WORM_THIRST_RATE * dt)

        # Cooldown progress
        self.reproduction_timer = max(0.0, self.reproduction_timer - dt)

        # Only count starvation when hunger is effectively full; when
        # hunger is moderate we let starvation recover faster.
        if self.hunger >= 0.95:
            self.starvation_time += dt
        else:
            self.starvation_time = max(0.0, self.starvation_time - dt)

        if self.thirst >= 0.95:
            self.dehydration_time += dt
        else:
            self.dehydration_time = max(0.0, self.dehydration_time - dt)

    def choose_state(self) -> None:
        """Pick a behaviour based on needs; water takes priority."""
        if self.is_dead:
            self.state = WormState.DEAD
            return

        if self.thirst >= settings.WORM_THIRST_THRESHOLD:
            self.state = WormState.SEEKING_WATER
            return

        if self.hunger >= settings.WORM_HUNGER_THRESHOLD:
            self.state = WormState.SEEKING_FOOD
            return

        self.state = WormState.WANDERING

    def sleep(self) -> None:
        self.target_x = None
        self.target_y = None
        self.wander_timer = 0.0

    def move_towards(self, target_x: float, target_y: float, dt: float) -> bool:
        dx = target_x - self.x
        dy = target_y - self.y

        dist = math.hypot(dx, dy)
        if dist <= 0.15:
            self.x = target_x
            self.y = target_y
            return True

        nx = dx / dist
        ny = dy / dist

        speed = settings.WORM_MOVE_SPEED

        self.x += nx * speed * dt
        self.y += ny * speed * dt

        if abs(nx) > 0.05:
            self.direction = 1.0 if nx > 0 else -1.0

        return False

    def wander(self, dt: float, width: int, height: int) -> None:
        self.wander_timer -= dt

        if self.wander_timer <= 0.0 or self.target_x is None or self.target_y is None:
            self.wander_timer = settings.WORM_WANDER_INTERVAL

            angle = (self.direction * 0.5) + (math.sin(self.age * 0.3) * 0.6)

            self.target_x = max(1.0, min(width - 2.0, self.x + math.cos(angle) * 6.0))
            self.target_y = max(1.0, min(height - 2.0, self.y + math.sin(angle) * 3.0))

        self.move_towards(self.target_x, self.target_y, dt)

    def eat(self) -> None:
        # Eating gives a larger, immediate benefit and reduces starvation
        self.hunger = max(0.0, self.hunger - settings.WORM_FOOD_AMOUNT)
        self.starvation_time = max(0.0, self.starvation_time - 5.0)

    def drink(self) -> None:
        self.thirst = max(0.0, self.thirst - settings.WORM_WATER_AMOUNT)
        self.dehydration_time = max(0.0, self.dehydration_time - 5.0)

    def grow_step(self, dt: float) -> None:
        if self.is_dead:
            return

        self.growth = min(settings.WORM_MATURE_SIZE, self.growth + settings.WORM_GROWTH_RATE * dt)

    def can_reproduce(self) -> bool:
        return (
            not self.is_dead
            and self.age >= settings.WORM_REPRODUCTION_AGE
            and self.growth >= settings.WORM_REPRODUCTION_GROWTH_THRESHOLD
            and self.hunger < 0.6
            and self.thirst < 0.6
            and self.reproduction_timer <= 0.0
        )

    def reproduce(self) -> None:
        # start cooldown and apply a small cost
        self.reproduction_timer = settings.WORM_REPRODUCTION_COOLDOWN
        self.hunger = min(1.0, self.hunger + 0.18)
        self.thirst = min(1.0, self.thirst + 0.10)

    def die(self) -> None:
        if self.is_dead:
            return

        self.state = WormState.DEAD
        self.target_x = None
        self.target_y = None

    def update_rot(self, dt: float) -> None:
        if not self.is_dead:
            return

        self.rot = min(1.0, self.rot + dt / settings.WORM_ROT_DURATION)

    def should_remove(self) -> bool:
        return self.is_dead and self.rot >= 1.0

    @property
    def is_dead(self) -> bool:
        return self.state == WormState.DEAD

    @property
    def condition(self) -> float:
        if self.is_dead:
            return 0.0
        return max(0.0, min(1.0, 1.0 - max(self.hunger, self.thirst)))

    @property
    def size(self) -> float:
        return 0.45 + (0.55 * self.growth)