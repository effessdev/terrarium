# 🌿 Terrarium (by Sonnet 5)

A 2D terrarium simulation in Python and Pygame. Sand, soil, rocks and ponds, seven plant species and four insect species, a water cycle, and a day/night cycle. Every run generates a different world and a different colour palette.

![Terrarium screenshot](assets/screenshot.png)

## Features

- **Terrain:** Sand strata, fertile soil, rocks and ponds, simulated as falling-sand physics. Wet soil holds tunnels open, while dry sand slumps into piles.
- **Plants:** Grass, fern, flower, moss, mushroom, bush and cactus. They grow, compete for space and light, reproduce by seed or spore, die, and rot into detritus, which later turns into fertile soil.
- **Insects:** Ants, beetles, butterflies and fireflies. They eat, mate, age, die, and leave corpses that rot.
- **Insects that move soil:** Ants dig tunnels, carry grains to the surface and build mounds. Dry sand around a mound slumps, while damp soil keeps its tunnels open.
- **Water cycle:** Ponds and damp ground evaporate into mist. Mist rises and condenses on the glass lid, and droplets drip back down as rain. Plants take up water through their roots and release some back as vapour.
- **Day/night cycle:** Sun and moon arcs, twinkling stars, dawn and dusk colours, and varying cloud cover. Flowers close at night, mushrooms fruit in the dark, and fireflies glow.
- **Unique every run:** The terrain, pond count, dryness, plant mix, starting time of day, and colour palette are re-rolled each run. Palettes come from six hand-tuned themes with small random shifts. A perceptual contrast check rejects any palette where important colours would be hard to tell apart.
- **Light on hardware:** CPU-only rendering with the world simulated on a 320×180 grid (4 px per cell) using vectorised NumPy. No GPU is needed.

## Quick start

```bash
pip install -r requirements.txt
python main.py
```

Requires Python 3.9+ (developed on 3.12), `pygame >= 2.5` and `numpy >= 1.24`.

### Command-line options

| Option          | Description                                                                                        |
| --------------- | -------------------------------------------------------------------------------------------------- |
| `--seed N`      | Reproduce a specific terrarium (the seed is shown in the HUD and printed on start).                |
| `--cell-size N` | Pixels per simulation cell. Default is `4`; use `5` for a lighter load. The window stays 1280×720. |
| `--selftest N`  | Headless: run N ticks, print statistics and save a screenshot.                                     |

## Controls

| Key / Mouse | Action                                                     |
| ----------- | ---------------------------------------------------------- |
| `Space`     | Pause / resume                                             |
| `+` / `-`   | Change simulation speed (0.5x to 8x)                       |
| `H`         | Toggle HUD                                                 |
| `F1`        | Toggle help                                                |
| `R`         | Generate a new world                                       |
| `S`         | Save a screenshot (PNG in the current directory)           |
| `1`–`7`     | Select tool: sand, soil, water, rock, erase, plant, insect |
| Left mouse  | Use the selected tool                                      |
| Right mouse | Erase                                                      |
| Mouse wheel | Change brush size                                          |
| `Esc`       | Quit                                                       |

## Project structure

Each concern lives in its own package, so several people can work in parallel with few merge conflicts.

| Folder                  | Responsibility                                                                                  |
| ----------------------- | ----------------------------------------------------------------------------------------------- |
| `terrarium/core/`       | Seeded RNG, event bus, `System` base class, `SimContext`, fixed-step `Simulation`               |
| `terrarium/world/`      | `Grid` (stacked NumPy layers) and material property tables                                      |
| `terrarium/palette/`    | Themes, colour maths, palette generator with contrast validation                                |
| `terrarium/physics/`    | Vectorised sand and water movement, ground moisture                                             |
| `terrarium/climate/`    | Day clock, weather, vapour field, water cycle                                                   |
| `terrarium/flora/`      | `Plant` life cycle, seeds, and one file per species in `species/`                               |
| `terrarium/fauna/`      | `Insect`, reusable behaviours in `behaviors/`, and one file per species in `species/`           |
| `terrarium/ecology/`    | Corpses, decomposition, population director                                                     |
| `terrarium/generation/` | World-generation pipeline: terrain, rocks, ponds, moisture, populate                            |
| `terrarium/render/`     | Low-resolution layer stack (sky, terrain, plants, mist, lighting) plus full-resolution overlays |
| `terrarium/ui/`         | HUD, input handling, paint tools                                                                |
| `terrarium/builder.py`  | Composition root: the only file that knows every system                                         |
| `terrarium/config.py`   | All global tunables                                                                             |
| `tests/`, `tools/`      | Smoke tests and a long-run ecosystem check                                                      |

### How it fits together

- The simulation is a list of **systems** (gravity, moisture, water cycle, seeds, flora, fauna, corpses, decomposition, ecology) updated in a fixed order at 30 ticks per simulated second.
- All world state lives in the `Grid`: material, wetness, tint, and the plant layers.
- Systems talk through the shared `SimContext` or the event bus, not by importing each other.
- The renderer only reads state. It draws a small low-resolution frame with NumPy, scales it up, then adds insects, glow, glass and the HUD.

## Extending the project

- **New plant:** Add `terrarium/flora/species/yourplant.py`, subclass `PlantSpecies` and decorate it with `@register`. It is auto-discovered, so nothing else needs editing.
- **New insect:** Add `terrarium/fauna/species/yourbug.py`, subclass `InsectSpecies`, list its behaviours in priority order, and implement `draw`. It is auto-discovered too.
- **New diet:** Write a `FoodSource` (two methods) in `fauna/behaviors/feeding.py` and add it to a species' `Feed([...])` list.
- **New behaviour:** Subclass `Behavior` in `fauna/behaviors/`. The first behaviour in a species' list that returns `True` wins the step.
- **New system:** Subclass `System`, then register it in `builder.py` at the right place in the update order.
- **New world-generation step:** Write a function `step(ctx)` and add it to `PIPELINE` in `generation/worldgen.py`.
- **New palette theme:** Add a `Theme` to `palette/themes.py`.
- **New material:** Add it to `Mat` and to every table in `world/materials.py`. An assertion catches a forgotten table. Then give it a colour in `render/layers/terrain.py`.
- **Tuning:** Global numbers (day length, evaporation, population caps, and so on) are in `config.py`. Species-specific numbers sit at the top of each species class.

## Testing

```bash
pip install pytest
python -m pytest -q tests              # smoke tests (headless)
python tools/stability.py 1 4          # long-run ecosystem check: seed 1, 4 simulated days
```

Runs are reproducible per seed. The tests check that the same seed gives the same world state after 200 ticks.

## Performance notes

- In my development sandbox (a single slow core, headless), a simulation tick takes about 4 ms and a rendered frame about 8.5 ms. At 1x speed the simulation needs 30 ticks per second, so 60 FPS should be comfortable on a modern laptop CPU such as a Ryzen 7 7730U.
- I have not benchmarked it on that hardware. If it ever stutters, use `--cell-size 5`.
- At high speed multipliers the app limits ticks per frame and drops the backlog rather than freezing.

## Known limitations

- **Ponds shrink:** Ponds lose much of their water during the first simulated day as the surrounding dry sand soaks it up. Rain refills a smaller reservoir, and on some seeds the rain cycle is weak.
- **No predators:** Insect populations are limited by food and crowding, not by hunting.
- **Long-run balance:** Populations were checked for a few simulated days on several seeds and stayed alive with rescue of extinct species enabled. Longer runs may still go quiet on some seeds. Rescue can be disabled in `EcologyConfig`.
- **Tools:** The paint tools are basic.
