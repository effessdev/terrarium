"""Random number generation for the simulation."""

from __future__ import annotations

import random
import time


class Randomizer:
    """
    Centralized random number generator.

    A new seed is generated automatically for every application launch.
    The seed can later be exposed through the UI or command line to
    reproduce interesting simulations.
    """

    def __init__(self, seed: int | None = None) -> None:
        if seed is None:
            seed = self._generate_seed()

        self.seed = seed
        self._random = random.Random(seed)

    @staticmethod
    def _generate_seed() -> int:
        """Generate a reasonably varied integer seed."""
        return time.time_ns() & 0xFFFFFFFF

    def random(self) -> float:
        """Return a random float in [0.0, 1.0)."""
        return self._random.random()

    def uniform(self, minimum: float, maximum: float) -> float:
        """Return a random float between minimum and maximum."""
        return self._random.uniform(minimum, maximum)

    def randint(self, minimum: int, maximum: int) -> int:
        """Return a random integer between minimum and maximum."""
        return self._random.randint(minimum, maximum)

    def choice(self, sequence):
        """Choose one item from a non-empty sequence."""
        return self._random.choice(sequence)

    def chance(self, probability: float) -> bool:
        """
        Return True with the specified probability.

        Example:
            chance(0.25) -> approximately 25% of calls return True.
        """
        if not 0.0 <= probability <= 1.0:
            raise ValueError("probability must be between 0.0 and 1.0")

        return self._random.random() < probability
