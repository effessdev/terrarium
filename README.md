# Terrarium

A 2D pygame terrarium (1280x720): sand, soil, rocks, ponds, 7 plant species, 4 insect
species, water cycle (evaporation -> mist -> lid condensation -> rain), day/night cycle,
rot -> soil, insects that dig and carry soil. Every run rolls a new world **and** a new
(harmonious) colour palette.

    pip install -r requirements.txt
    python main.py                 # random world
    python main.py --seed 42       # reproduce one
    python main.py --cell-size 5   # lighter on weak machines (default 4)

Keys: SPACE pause, +/- speed, H hud, F1 help, R new world, S screenshot, 1-5 paint tools
(sand/soil/water/rock/erase), mouse = paint, wheel = brush size.

## Architecture (one concern per folder)

| Folder | Responsibility |
|---|---|
| `core/` | RNG, event bus, `System` base class, `SimContext`, fixed-step `Simulation` |
| `world/` | `Grid` (numpy layers) and material property tables |
| `palette/` | themes, colour maths, palette generator with contrast validation |
| `physics/` | vectorised sand/water gravity, ground moisture |
| `climate/` | day clock, weather, vapour field, water cycle |
| `flora/` | `Plant` life cycle, seeds, species (`flora/species/*.py`, auto-registered) |
| `fauna/` | `Insect`, behaviours (`behaviors/`), species (`fauna/species/*.py`, auto-registered) |
| `ecology/` | corpses, decomposition, population director (rescue of extinct species) |
| `generation/` | world-gen pipeline: terrain, rocks, ponds, moisture, populate |
| `render/` | low-res layer stack (sky, terrain, plants, mist, lighting) + full-res overlays |
| `ui/` | HUD, input, paint tools |
| `builder.py` | composition root: the only file that knows every system |

## Extending
* **New plant**: add `flora/species/yourplant.py`, subclass `PlantSpecies`, decorate with `@register`.
* **New insect**: add `fauna/species/yourbug.py`, subclass `InsectSpecies`, list behaviours, implement `draw`.
* **New diet**: write a `FoodSource` in `fauna/behaviors/feeding.py`.
* **New system**: subclass `System`, register it in `builder.py`.
* **New world-gen step**: write `step(ctx)` and add it to `PIPELINE` in `generation/worldgen.py`.
* **New palette theme**: add a `Theme` to `palette/themes.py`.
* All global tunables live in `config.py`; species numbers sit inside each species class.

Known simplifications: ponds slowly soak into the ground (rain refills them), no predators,
tool set is minimal.
