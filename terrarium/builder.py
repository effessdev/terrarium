"""Composition root: creates the context, registers systems, generates the world.

This is the only file that knows *all* systems.  To add a system: instantiate it here in
the right place of the update order.
"""
from __future__ import annotations

import random

from .climate.clock import DayClock
from .climate.water_cycle import WaterCycleSystem
from .climate.weather import Weather
from .config import Config
from .core.context import SimContext
from .core.rng import RNG
from .core.simulation import Simulation
from .ecology.corpses import CorpseSystem
from .ecology.decomposition import DecompositionSystem
from .ecology.director import EcologyDirector
from .fauna.system import FaunaSystem
from .flora.seeds import SeedSystem
from .flora.system import FloraSystem
from .generation.params import roll_params
from .generation.worldgen import generate_world
from .palette.generator import generate_palette
from .physics.gravity import GravitySystem
from .physics.moisture import MoistureSystem


def new_seed() -> int:
    return random.SystemRandom().randrange(1, 2 ** 31)


def build_simulation(config: Config | None = None, seed: int | None = None) -> Simulation:
    config = config or Config()
    seed = new_seed() if seed is None else int(seed)
    rng = RNG(seed)
    palette = generate_palette(rng.child("palette"))
    ctx = SimContext(config, rng, palette)
    ctx.params = roll_params(rng.child("world"))
    sim = Simulation(ctx)
    ctx.sim = sim            # type: ignore[attr-defined]  (used by the generation pipeline)

    # order matters: time -> weather -> physics -> climate -> life -> ecology
    ctx.clock = sim.add(DayClock(ctx, start_phase=ctx.params.start_phase))
    ctx.weather = sim.add(Weather(ctx))
    sim.add(GravitySystem(ctx))
    sim.add(MoistureSystem(ctx))
    ctx.water_cycle = sim.add(WaterCycleSystem(ctx))
    ctx.seeds = sim.add(SeedSystem(ctx))
    ctx.flora = sim.add(FloraSystem(ctx))
    ctx.fauna = sim.add(FaunaSystem(ctx))
    ctx.corpses = sim.add(CorpseSystem(ctx))
    sim.add(DecompositionSystem(ctx))
    ctx.ecology = sim.add(EcologyDirector(ctx))

    # weather needs one update so temperature / light are valid before the first tick
    ctx.clock.update(0.0)
    ctx.weather.update(0.0)
    generate_world(ctx)
    ctx.ecology.update(0.0)
    return sim
