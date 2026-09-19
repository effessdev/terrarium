# TODO

This file should be constantly updated.

## Phase 1 — Project Foundation

- [x] Create basic Pygame application
- [x] Create modular package structure
- [x] Add centralized application settings
- [x] Add main game loop
- [x] Add fixed-timestep simulation clock
- [x] Add render FPS limiting
- [x] Add centralized random number generator
- [x] Generate a unique seed for each run
- [x] Display basic debug information
- [x] Cleanly shut down Pygame

## Phase 2 — Basic World

- [x] Add world grid
- [x] Add configurable world cell size
- [x] Add terrain cell data structure
- [x] Add terrain types:
  - [x] Air
  - [x] Soil
  - [x] Sand
  - [x] Water
  - [x] Rock

- [x] Generate uneven terrain
- [x] Generate soil and sand layers
- [x] Generate shallow water regions
- [x] Generate rocks
- [x] Render terrain
- [x] Connect world generation to the main game

## Phase 3 — Palette and Day/Night

- [x] Add procedural palette generation
- [x] Keep generated colors visually coherent
- [x] Vary palette between runs
- [x] Add day/night cycle
- [x] Add configurable simulated day length
- [x] Add simulated time-of-day
- [x] Add daylight factor
- [x] Add basic global night lighting
- [x] Add sun/moon indicator
- [x] Display simulated time in debug information

---

# Phase 4 — Plants

- [ ] Add base plant entity
- [ ] Add simple plant state/data
- [ ] Add plant positioning
- [ ] Add plant renderer
- [ ] Add first plant species
- [ ] Add second plant species
- [ ] Add third plant species
- [ ] Add plant growth
- [ ] Make growth depend on environmental conditions
- [ ] Add water consumption
- [ ] Add nutrient consumption
- [ ] Add basic plant reproduction
- [ ] Add plant lifespan
- [ ] Add plant death
- [ ] Add basic plant variation between runs

# Phase 5 — Soil and Resources

- [ ] Add meaningful soil moisture simulation
- [ ] Add soil nutrient changes
- [ ] Allow plants to affect soil
- [ ] Allow water to affect soil moisture
- [ ] Add simple resource regeneration/cycling
- [ ] Keep resource simulation lightweight enough for the target hardware

# Phase 6 — Water Cycle

- [ ] Add water movement
- [ ] Add basic evaporation
- [ ] Add atmospheric moisture representation if needed
- [ ] Add condensation/precipitation
- [ ] Connect rainfall to terrain
- [ ] Connect water availability to plants
- [ ] Keep the water model simple rather than physically accurate

# Phase 7 — Insects

- [ ] Add base insect entity
- [ ] Add insect movement
- [ ] Add simple movement variation
- [ ] Add insect renderer
- [ ] Add first insect type
- [ ] Add second insect type
- [ ] Add third insect type
- [ ] Allow insects to interact with terrain
- [ ] Allow insects to disturb/move soil
- [ ] Add insect food/resource needs
- [ ] Add insect reproduction
- [ ] Add insect lifespan
- [ ] Add insect death

# Phase 8 — Ecosystem Interactions

- [ ] Plants interact with water
- [ ] Plants interact with soil nutrients
- [ ] Insects interact with plants
- [ ] Insects interact with terrain
- [ ] Dead organisms become decomposable material
- [ ] Add decomposition
- [ ] Return nutrients to soil through decomposition
- [ ] Connect decomposition to plant growth
- [ ] Ensure interactions remain simple and understandable

# Phase 9 — Environmental Effects

- [ ] Make day/night affect plant behavior
- [ ] Make day/night affect insect behavior
- [ ] Add simple temperature/environment factor if useful
- [ ] Add environmental stress
- [ ] Add weather variation
- [ ] Make environmental conditions influence reproduction
- [ ] Make environmental conditions influence mortality

# Phase 10 — Population and Simulation Stability

- [ ] Add basic population tracking
- [ ] Prevent runaway population growth
- [ ] Prevent immediate ecosystem collapse
- [ ] Add lightweight spatial lookup/grid if needed
- [ ] Remove dead entities efficiently
- [ ] Avoid unnecessary per-pixel simulation
- [ ] Test larger populations
- [ ] Check long-running simulation performance

# Phase 11 — Visual Polish

- [ ] Improve plant visuals
- [ ] Improve insect visuals
- [ ] Improve rocks
- [ ] Improve water appearance
- [ ] Add subtle environmental effects
- [ ] Improve day/night transitions
- [ ] Add small visual variation to organisms
- [ ] Keep the visual style coherent with procedural palettes

# Phase 12 — User Interface

- [ ] Improve debug HUD
- [ ] Display simulation time
- [ ] Display population counts
- [ ] Display important environmental information
- [ ] Add pause/unpause
- [ ] Add simulation speed controls
- [ ] Add restart/regenerate world
- [ ] Show current random seed
- [ ] Allow reproducing a simulation using a seed

# Phase 13 — Testing and Cleanup

- [ ] Test repeated world generation
- [ ] Test repeated simulation runs
- [ ] Verify different seeds produce meaningful variation
- [ ] Check for entity leaks
- [ ] Check for runaway populations
- [ ] Check long-running simulation stability
- [ ] Check 60 FPS target
- [ ] Profile expensive systems
- [ ] Remove unnecessary complexity
- [ ] Keep modules small and focused
- [ ] Document important systems
- [ ] Verify clean startup from a fresh checkout

# Phase 14 — Finalization

- [ ] Review project architecture
- [ ] Remove unused code
- [ ] Remove temporary/debug-only code where appropriate
- [ ] Finalize configuration values
- [ ] Finalize simulation balance
- [ ] Final performance pass
- [ ] Final visual pass
- [ ] Create a reproducible release build/setup
- [ ] Update project documentation
- [ ] Mark completed project milestones

---

# Rules for Updating This TODO

- Keep completed work checked.
- Keep unfinished work unchecked.
- Remove TODO items only when they are no longer relevant.
- Keep this file aligned with the actual project state.
- Update this file whenever a development phase is completed.
- Prefer small, concrete tasks over vague large tasks.
- Do not add unnecessary architecture just to satisfy the TODO.
