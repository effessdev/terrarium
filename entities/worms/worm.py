"""Worm entity and its basic life cycle."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math

from config import settings


class WormState(Enum):
    """Current behavioral state of a worm."""

    WANDERING = "wandering"
    SEEKING_FOOD = "seeking_food"
    SEEKING_WATER = "seeking_water"
    SLEEPING = "sleeping"
    DEAD = "dead"


@dataclass
class Worm:
    """A small worm living inside the terrarium."""

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
        """Increase hunger and thirst over time."""
        if self.is_dead:
            return

        self.age += dt

        self.hunger = min(
            1.0,
            self.hunger
            + settings.WORM_HUNGER_RATE * dt,
        )

        self.thirst = min(
            1.0,
            self.thirst
            + settings.WORM_THIRST_RATE * dt,
        )

        self.reproduction_timer = max(
            0.0,
            self.reproduction_timer - dt,
        )

        if self.hunger >= 0.8:
            self.starvation_time += dt
        else:
            self.starvation_time = max(
                0.0,
                self.starvation_time - dt * 0.5,
            )

        if self.thirst >= 0.8:
            self.dehydration_time += dt
        else:
            self.dehydration_time = max(
                0.0,
                self.dehydration_time - dt * 0.5,
            )

    def choose_state(self) -> None:
        """Choose behavior based on current condition."""
        if self.is_dead:
            self.state = WormState.DEAD
            return

        if self.thirst >= settings.WORM_THIRST_THRESHOLD:
            self.state = WormState.SEEKING_WATER
            return

        if self.hunger >= settings.WORM_HUNGER_THRESHOLD:
            self.state = WormState.SEEKING_FOOD
            return

        self.state = WormState.SLEEPING

    def sleep(self) -> None:
        """Settle into a resting state without drifting."""
        self.target_x = None
        self.target_y = None
        self.wander_timer = 0.0

    def move_towards(
        self,
        target_x: float,
        target_y: float,
        dt: float,
    ) -> bool:
        """
        Move toward a target.

        Returns True when the worm reaches the target.
        """
        delta_x = target_x - self.x
        delta_y = target_y - self.y

        distance = math.hypot(
            delta_x,
            delta_y,
        )

        if distance <= 0.15:
            self.x = target_x
            self.y = target_y
            return True

        direction_x = delta_x / distance
        direction_y = delta_y / distance

        self.x += (
            direction_x
            * settings.WORM_MOVE_SPEED
            * dt
        )

        self.y += (
            direction_y
            * settings.WORM_MOVE_SPEED
            * dt
        )

        if abs(direction_x) > 0.05:
            self.direction = (
                1.0
                if direction_x > 0.0
                else -1.0
            )

        return False

    def wander(
        self,
        dt: float,
        width: int,
        height: int,
    ) -> None:
        """Move slowly in a random-looking direction."""
        self.wander_timer -= dt

        if (
            self.wander_timer <= 0.0
            or self.target_x is None
            or self.target_y is None
        ):
            self.wander_timer = (
                settings.WORM_WANDER_INTERVAL
            )

            angle = (
                self.direction * 0.5
            )

            self.target_x = max(
                1.0,
                min(
                    width - 2.0,
                    self.x
                    + math.cos(angle) * 4.0,
                ),
            )

            self.target_y = max(
                1.0,
                min(
                    height - 2.0,
                    self.y
                    + math.sin(angle) * 2.0,
                ),
            )

        self.move_towards(
            self.target_x,
            self.target_y,
            dt,
        )

    def eat(self) -> None:
        """Eat some food and become less hungry."""
        self.hunger = max(
            0.0,
            self.hunger
            - settings.WORM_FOOD_AMOUNT,
        )

    def drink(self) -> None:
        """Drink water and become less thirsty."""
        self.thirst = max(
            0.0,
            self.thirst
            - settings.WORM_WATER_AMOUNT,
        )

    def grow_step(self, dt: float) -> None:
        """Grow while the worm is alive."""
        if self.is_dead:
            return

        self.growth = min(
            settings.WORM_MATURE_SIZE,
            self.growth
            + settings.WORM_GROWTH_RATE * dt,
        )

    def can_reproduce(self) -> bool:
        """Return whether this worm can currently reproduce."""
        return (
            not self.is_dead
            and self.age >= settings.WORM_REPRODUCTION_AGE
            and self.growth >= 0.8
            and self.hunger < 0.35
            and self.thirst < 0.35
            and self.reproduction_timer <= 0.0
        )

    def reproduce(self) -> None:
        """Start the reproduction cooldown."""
        self.reproduction_timer = (
            settings.WORM_REPRODUCTION_COOLDOWN
        )

        self.hunger = min(
            1.0,
            self.hunger + 0.12,
        )

        self.thirst = min(
            1.0,
            self.thirst + 0.08,
        )

    def die(self) -> None:
        """Kill the worm and begin decomposition."""
        if self.is_dead:
            return

        self.state = WormState.DEAD
        self.target_x = None
        self.target_y = None

    def update_rot(self, dt: float) -> None:
        """Progressively decompose the dead worm."""
        if not self.is_dead:
            return

        self.rot = min(
            1.0,
            self.rot
            + dt / settings.WORM_ROT_DURATION,
        )

    def should_remove(self) -> bool:
        """Return True once the corpse has completely rotted."""
        return self.is_dead and self.rot >= 1.0

    @property
    def is_dead(self) -> bool:
        """Return whether the worm has died."""
        return self.state == WormState.DEAD

    @property
    def condition(self) -> float:
        """
        Return a simple health/condition value.

        1.0 is healthy, 0.0 is extremely distressed.
        """
        if self.is_dead:
            return 0.0

        return max(
            0.0,
            min(
                1.0,
                1.0
                - max(
                    self.hunger,
                    self.thirst,
                ),
            ),
        )

    @property
    def size(self) -> float:
        """Return visual size based on growth."""
        return 0.45 + (
            0.55 * self.growth
        )