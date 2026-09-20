"""Step 5: seed the terrarium with plants and insects."""
from __future__ import annotations

from ..fauna.registry import all_species as all_insects
from ..flora.registry import all_species as all_plants
from ..world.materials import ROCK


def populate(ctx) -> None:
    rng, p, cfg = ctx.rng, ctx.params, ctx.config.worldgen
    species = all_plants()
    weights = [max(0.01, s.initial_weight * p.plant_mix.get(s.name, 1.0)) for s in species]
    target = rng.randint(*cfg.initial_plants)
    placed = 0
    for _ in range(target * 6):
        if placed >= target:
            break
        sp = rng.weighted_choice(species, weights)
        spot = ctx.flora.find_spot(sp, tries=25)
        if spot is None:
            continue
        frac = rng.uniform(0.15, 0.8)
        plant = ctx.flora.spawn(sp, *spot, steps=int(sp.max_steps * rng.uniform(0.25, 1.0)) + 1, age_frac=frac * 0.6)
        if plant is not None:
            placed += 1
    # guarantee some moss on bare rock
    moss = next((s for s in species if s.name == "moss"), None)
    if moss is not None:
        g = ctx.grid
        for _ in range(60):
            spot = ctx.flora.find_spot(moss, tries=10)
            if spot and g.mat_at(spot[0], spot[1] + 1) == ROCK:
                ctx.flora.spawn(moss, *spot, steps=rng.randint(4, 20))

    total = rng.randint(*cfg.initial_insects)
    insects = all_insects()
    shares = [sum(s.initial_count) / 2.0 for s in insects]
    scale = total / sum(shares)
    for sp, share in zip(insects, shares):
        for _ in range(max(2, int(round(share * scale)))):
            spot = ctx.fauna.find_spot(sp)
            if spot:
                ctx.fauna.spawn(sp, *spot)
