"""Headless smoke tests:  python -m pytest -q"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from terrarium.builder import build_simulation
from terrarium.palette.generator import generate_palette
from terrarium.core.rng import RNG


def test_palettes_valid():
    for s in range(30):
        assert generate_palette(RNG(s)).name


def test_simulation_runs_and_is_reproducible():
    a, b = build_simulation(seed=7), build_simulation(seed=7)
    for _ in range(200):
        a.tick(); b.tick()
    assert (a.ctx.grid.mat == b.ctx.grid.mat).all()
    assert a.ctx.stats["insect_total"] > 0
