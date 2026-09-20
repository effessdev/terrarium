"""Seeded random number source.

Two streams are exposed because they serve different needs:
  * ``py``  - ``random.Random``: very fast for scalar decisions inside entity logic.
  * ``np``  - ``numpy.random.Generator``: for vectorised work on the grid.

``child(label)`` derives an independent, reproducible RNG (used e.g. by the palette
generator so that adding a new random call elsewhere never changes the colours).
"""
from __future__ import annotations

import hashlib
import random

import numpy as np


class RNG:
    def __init__(self, seed: int) -> None:
        self.seed = int(seed)
        self.py = random.Random(self.seed)
        self.np = np.random.default_rng(self.seed)

    def child(self, label: str) -> "RNG":
        digest = hashlib.sha256(f"{self.seed}:{label}".encode()).digest()
        return RNG(int.from_bytes(digest[:8], "little"))

    # thin scalar helpers ------------------------------------------------
    def random(self) -> float:
        return self.py.random()

    def chance(self, p: float) -> bool:
        return self.py.random() < p

    def uniform(self, a: float, b: float) -> float:
        return self.py.uniform(a, b)

    def randint(self, a: int, b: int) -> int:
        return self.py.randint(a, b)

    def gauss(self, mu: float = 0.0, sigma: float = 1.0) -> float:
        return self.py.gauss(mu, sigma)

    def choice(self, seq):
        return self.py.choice(seq)

    def sign(self) -> int:
        return 1 if self.py.random() < 0.5 else -1

    def weighted_choice(self, items, weights):
        return self.py.choices(items, weights=weights, k=1)[0]
