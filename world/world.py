"""Terrarium world."""

from __future__ import annotations

import math

from config import settings
from entities.plants.grass import Grass
from entities.plants.plant import Plant
from entities.worms.worm import Worm, WormState
from utils.randomizer import Randomizer
from world.generation import WorldGenerator
from world.terrain import TerrainCell, TerrainType


class World:
    """Contains the physical state of the terrarium."""

    def __init__(
        self,
        width: int,
        height: int,
        randomizer: Randomizer,
    ) -> None:
        self.width = width
        self.height = height

        self.randomizer = randomizer

        self.generator = WorldGenerator(
            randomizer
        )

        self.terrain: list[list[TerrainCell]] = []

        self.plants: list[Plant] = []
        self.worms: list[Worm] = []

        self.generate()

    def generate(self) -> None:
        """Generate a new world."""
        self.terrain = self.generator.generate(
            self.width,
            self.height,
        )

        self._generate_initial_plants()
        self._generate_initial_worms()

    def _generate_initial_plants(self) -> None:
        """Place a small number of initial plants."""
        self.plants.clear()

        attempts = self.randomizer.randint(
            8,
            14,
        )

        for _ in range(attempts):
            x = self.randomizer.randint(
                2,
                self.width - 3,
            )

            surface_y = self._find_surface_y(x)

            if surface_y is None:
                continue

            plant_y = surface_y

            if self.terrain[plant_y][x].terrain_type not in {
                TerrainType.SOIL,
                TerrainType.SAND,
            }:
                continue

            self.plants.append(
                Grass(
                    x=x,
                    y=plant_y,
                    growth=self.randomizer.uniform(
                        0.05,
                        0.95,
                    ),
                )
            )

    def _generate_initial_worms(self) -> None:
        """Place a small starting population of worms."""
        self.worms.clear()

        count = self.randomizer.randint(
            settings.INITIAL_WORM_COUNT_MIN,
            settings.INITIAL_WORM_COUNT_MAX,
        )

        attempts = count * 5

        for _ in range(attempts):
            if len(self.worms) >= count:
                break

            x = self.randomizer.randint(
                2,
                self.width - 3,
            )

            surface_y = self._find_surface_y(x)

            if surface_y is None:
                continue

            terrain = self.terrain[
                surface_y
            ][x].terrain_type

            if terrain not in {
                TerrainType.SOIL,
                TerrainType.SAND,
            }:
                continue

            self.worms.append(
                Worm(
                    x=float(x),
                    y=float(surface_y),
                    hunger=self.randomizer.uniform(
                        0.05,
                        0.25,
                    ),
                    thirst=self.randomizer.uniform(
                        0.05,
                        0.25,
                    ),
                    growth=self.randomizer.uniform(
                        0.20,
                        0.55,
                    ),
                    direction=(
                        1.0
                        if self.randomizer.chance(0.5)
                        else -1.0
                    ),
                )
            )

    def _find_surface_y(
        self,
        x: int,
    ) -> int | None:
        """Find the uppermost solid terrain cell."""
        for y in range(self.height):
            if self.terrain[y][x].is_solid():
                return y

        return None

    def _find_worm_surface_y(
        self,
        x: int,
    ) -> int | None:
        """
        Find the uppermost cell a worm can stand on.

        Unlike plants, worms treat water as walkable surface so they
        can reach a pool to drink. Air is never walkable.
        """
        for y in range(self.height):
            cell = self.terrain[y][x]

            if (
                cell.is_solid()
                or cell.is_water()
            ):
                return y

        return None

    def update(
        self,
        dt: float,
        daylight: float,
    ) -> None:
        """Update world-level simulation."""
        self._update_plants(dt, daylight)
        self._update_worms(dt)

    # ------------------------------------------------------------------
    # Plants
    # ------------------------------------------------------------------

    def _update_plants(
        self,
        dt: float,
        daylight: float,
    ) -> None:
        """Update plant growth and reproduction."""
        for plant in self.plants:
            moisture = self.terrain[
                plant.y
            ][plant.x].moisture

            nutrients = self.terrain[
                plant.y
            ][plant.x].nutrients

            plant.update(
                dt,
                daylight,
                moisture,
                nutrients,
            )

        self._handle_plant_reproduction()

    def _handle_plant_reproduction(self) -> None:
        """Let mature plants spread to nearby empty ground."""
        if len(self.plants) >= settings.PLANT_MAX_COUNT:
            return

        new_plants: list[Plant] = []

        for plant in self.plants:
            if not plant.can_reproduce():
                continue

            if (
                len(self.plants) + len(new_plants)
                >= settings.PLANT_MAX_COUNT
            ):
                break

            child = self._spawn_seedling(plant)

            if child is None:
                continue

            plant.reproduce()
            new_plants.append(child)

        self.plants.extend(new_plants)

    def _spawn_seedling(
        self,
        parent: Plant,
    ) -> Plant | None:
        """
        Try to create a seedling near the parent.

        Returns None when no valid nearby cell is available.
        """
        offsets = self._seedling_offsets()

        for offset_x in offsets:
            child_x = parent.x + offset_x

            if not 1 <= child_x < self.width - 1:
                continue

            surface_y = self._find_surface_y(child_x)

            if surface_y is None:
                continue

            cell = self.terrain[surface_y][child_x]

            if cell.terrain_type not in {
                TerrainType.SOIL,
                TerrainType.SAND,
            }:
                continue

            if self._plant_at(child_x, surface_y):
                continue

            return Grass(
                x=child_x,
                y=surface_y,
                growth=self.randomizer.uniform(
                    settings.PLANT_SEEDLING_GROWTH_MIN,
                    settings.PLANT_SEEDLING_GROWTH_MAX,
                ),
            )

        return None

    def _seedling_offsets(self) -> list[int]:
        """Return candidate horizontal offsets for a seedling."""
        max_offset = settings.PLANT_REPRODUCTION_RANGE

        offsets = [
            offset
            for offset in range(
                -max_offset,
                max_offset + 1,
            )
            if offset != 0
        ]

        self.randomizer.shuffle(offsets)

        return offsets

    def _plant_at(
        self,
        x: int,
        y: int,
    ) -> bool:
        """Return whether a plant already occupies the cell."""
        for plant in self.plants:
            if plant.x == x and plant.y == y:
                return True

        return False

    # ------------------------------------------------------------------
    # Worms
    # ------------------------------------------------------------------

    def _update_worms(self, dt: float) -> None:
        """Update worm needs, movement, feeding, reproduction and decay."""
        for worm in self.worms:
            if worm.is_dead:
                worm.update_rot(dt)
                continue

            worm.update_needs(dt)
            worm.grow_step(dt)

            if self._should_die(worm):
                worm.die()
                continue

            worm.choose_state()

            if worm.state == WormState.SEEKING_WATER:
                self._update_worm_water_behavior(
                    worm,
                    dt,
                )
            elif worm.state == WormState.SEEKING_FOOD:
                self._update_worm_food_behavior(
                    worm,
                    dt,
                )
            elif worm.state == WormState.WANDERING:
                worm.wander(
                    dt,
                    self.width,
                    self.height,
                )
            else:
                # Sleeping worms stay still.
                worm.sleep()

            self._keep_worm_on_ground(worm)

        self._apply_crowding_deaths()

        self._handle_worm_reproduction()

        self.worms = [
            worm
            for worm in self.worms
            if not worm.should_remove()
        ]

    def _apply_crowding_deaths(self) -> None:
        """
        Kill worms that are packed too tightly together.

        Density control that does not rely on a global population
        cap. Only living worms are counted, and corpses do not
        crowd out the living.
        """
        radius_squared = (
            settings.WORM_CROWDING_RADIUS
            * settings.WORM_CROWDING_RADIUS
        )

        limit = settings.WORM_CROWDING_LIMIT

        living = [
            worm
            for worm in self.worms
            if not worm.is_dead
        ]

        for index, worm in enumerate(living):
            neighbours = 0

            for other_index, other in enumerate(living):
                if other_index == index:
                    continue

                delta_x = other.x - worm.x
                delta_y = other.y - worm.y

                if (
                    delta_x * delta_x
                    + delta_y * delta_y
                    <= radius_squared
                ):
                    neighbours += 1

                    if neighbours >= limit:
                        worm.die()
                        break

    def _update_worm_water_behavior(
        self,
        worm: Worm,
        dt: float,
    ) -> None:
        """Find and drink from nearby water."""
        target = self._find_nearest_water(
            worm.x,
            worm.y,
        )

        if target is None:
            worm.wander(
                dt,
                self.width,
                self.height,
            )
            return

        target_x, target_y = target

        reached = worm.move_towards(
            target_x,
            target_y,
            dt,
        )

        if reached:
            worm.drink()

    def _update_worm_food_behavior(
        self,
        worm: Worm,
        dt: float,
    ) -> None:
        """Find and eat nearby plants."""
        target = self._find_nearest_plant(
            worm.x,
            worm.y,
        )

        if target is None:
            worm.wander(
                dt,
                self.width,
                self.height,
            )
            return

        plant_index, target_x, target_y = target

        reached = worm.move_towards(
            target_x,
            target_y,
            dt,
        )

        if reached:
            if 0 <= plant_index < len(self.plants):
                plant = self.plants[plant_index]

                plant.growth = max(
                    0.0,
                    plant.growth - 0.12,
                )

                worm.eat()

                if plant.growth <= 0.0:
                    self.plants.pop(
                        plant_index
                    )

    def _find_nearest_water(
        self,
        x: float,
        y: float,
    ) -> tuple[float, float] | None:
        """Find the nearest water cell within a useful range."""
        best_distance = math.inf
        best_target: tuple[float, float] | None = None

        # Allow worms to search a reasonably large area for water.
        # Previously a hard-coded small radius made distant pools
        # effectively invisible and led to mass dehydration.
        max_distance = max(self.width, self.height)

        min_x = max(
            0,
            int(x - max_distance),
        )

        max_x = min(
            self.width - 1,
            int(x + max_distance),
        )

        min_y = max(
            0,
            int(y - max_distance),
        )

        max_y = min(
            self.height - 1,
            int(y + max_distance),
        )

        for target_y in range(
            min_y,
            max_y + 1,
        ):
            for target_x in range(
                min_x,
                max_x + 1,
            ):
                cell = self.terrain[
                    target_y
                ][target_x]

                if not cell.is_water():
                    continue

                distance = math.hypot(
                    target_x - x,
                    target_y - y,
                )

                if distance < best_distance:
                    best_distance = distance
                    best_target = (
                        float(target_x),
                        float(target_y),
                    )

        return best_target

    def _find_nearest_plant(
        self,
        x: float,
        y: float,
    ) -> tuple[int, float, float] | None:
        """Find the nearest living plant."""
        best_distance = math.inf
        best_target = None

        for index, plant in enumerate(
            self.plants
        ):
            if plant.growth <= 0.0:
                continue

            distance = math.hypot(
                plant.x - x,
                plant.y - y,
            )

            if distance < best_distance:
                best_distance = distance
                best_target = (
                    index,
                    float(plant.x),
                    float(plant.y),
                )

        return best_target

    def _should_die(
        self,
        worm: Worm,
    ) -> bool:
        """Determine whether a worm has died."""
        if worm.age >= self._lifespan_for(worm):
            return True

        if (
            worm.starvation_time
            >= settings.WORM_STARVATION_LIMIT
        ):
            return True

        if (
            worm.dehydration_time
            >= settings.WORM_DEHYDRATION_LIMIT
        ):
            return True

        return False

    def _lifespan_for(
        self,
        worm: Worm,
    ) -> float:
        """Return a deterministic lifespan for this worm."""
        # The initial growth provides enough variation without storing
        # another per-worm random value.
        return (
            settings.WORM_MIN_LIFESPAN
            + (
                settings.WORM_MAX_LIFESPAN
                - settings.WORM_MIN_LIFESPAN
            )
            * worm.growth
        )

    def _handle_worm_reproduction(self) -> None:
        """Create offspring from nearby healthy worms."""
        new_worms: list[Worm] = []

        for index, first in enumerate(self.worms):
            if not first.can_reproduce():
                continue

            for second in self.worms[index + 1:]:
                if not second.can_reproduce():
                    continue

                distance = math.hypot(
                    first.x - second.x,
                    first.y - second.y,
                )

                if (
                    distance
                    > settings.WORM_REPRODUCTION_RANGE
                ):
                    continue

                first.reproduce()
                second.reproduce()

                child_x = (
                    first.x
                    + second.x
                ) / 2.0

                child_y = (
                    first.y
                    + second.y
                ) / 2.0

                child_x += self.randomizer.uniform(
                    -0.5,
                    0.5,
                )

                child_y += self.randomizer.uniform(
                    -0.3,
                    0.3,
                )

                new_worms.append(
                    Worm(
                        x=max(
                            1.0,
                            min(
                                self.width - 2.0,
                                child_x,
                            ),
                        ),
                        y=max(
                            1.0,
                            min(
                                self.height - 2.0,
                                child_y,
                            ),
                        ),
                        hunger=self.randomizer.uniform(
                            0.0,
                            0.12,
                        ),
                        thirst=self.randomizer.uniform(
                            0.0,
                            0.12,
                        ),
                        growth=self.randomizer.uniform(
                            0.08,
                            0.18,
                        ),
                        direction=(
                            1.0
                            if self.randomizer.chance(0.5)
                            else -1.0
                        ),
                    )
                )

                break

        self.worms.extend(new_worms)

    def _keep_worm_on_ground(
        self,
        worm: Worm,
    ) -> None:
        """
        Keep a worm inside the world and standing on the surface.

        Worms cannot fly: their vertical position is always snapped
        to the topmost walkable cell (solid ground or water) in the
        column they currently occupy.
        """
        worm.x = max(
            1.0,
            min(
                self.width - 2.0,
                worm.x,
            ),
        )

        column = int(worm.x)

        surface_y = self._find_worm_surface_y(column)

        if surface_y is not None:
            worm.y = float(surface_y)

        # Ensure the worm doesn't occupy the same integer cell as
        # any other worm. If the current column is already taken,
        # nudge the worm left/right to the nearest free column.
        col = int(worm.x)
        row = int(worm.y)

        occupied = False
        for other in self.worms:
            if other is worm:
                continue
            if int(other.x) == col and int(other.y) == row:
                occupied = True
                break

        if occupied:
            found = False
            for offset in range(1, 4):
                for direction in (-1, 1):
                    new_col = col + direction * offset
                    if not 1 <= new_col < self.width - 1:
                        continue

                    new_surface = self._find_worm_surface_y(new_col)
                    if new_surface is None:
                        continue

                    collision = False
                    for other in self.worms:
                        if other is worm:
                            continue
                        if int(other.x) == new_col and int(other.y) == new_surface:
                            collision = True
                            break

                    if not collision:
                        worm.x = float(max(1.0, min(self.width - 2.0, new_col)))
                        worm.y = float(new_surface)
                        found = True
                        break

                if found:
                    break

        worm.y = max(
            1.0,
            min(
                self.height - 2.0,
                worm.y,
            ),
        )