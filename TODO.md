# TODO

This file should be constantly updated.

## Phase 4 — Plants

- Add second plant species
- Add third plant species
- Make growth depend more meaningfully on environmental conditions
- Add water consumption
- Add nutrient consumption
- Add basic plant reproduction
- Add plant lifespan
- Add plant death

## Phase 5 — Soil and Resources

- Add meaningful soil moisture simulation
- Add soil nutrient changes
- Allow plants to affect soil
- Allow water to affect soil moisture
- Add simple resource regeneration/cycling
- Keep resource simulation lightweight enough for the target hardware

## Phase 6 — Water Cycle

- Add water movement
- Add basic evaporation
- Add atmospheric moisture representation if needed
- Add condensation/precipitation
- Connect rainfall to terrain
- Connect water availability to plants
- Keep the water model simple rather than physically accurate

## Phase 7 — Insects

- Add base insect entity
- Add insect movement
- Add simple movement variation
- Add insect renderer
- Add first insect type
- Add second insect type
- Add third insect type
- Allow insects to interact with terrain
- Allow insects to disturb/move soil
- Add insect food/resource needs
- Add insect reproduction
- Add insect lifespan
- Add insect death

## Phase 8 — Ecosystem Interactions

- Plants interact with water
- Plants interact with soil nutrients
- Insects interact with plants
- Insects interact with terrain
- Dead organisms become decomposable material
- Add decomposition
- Return nutrients to soil through decomposition
- Connect decomposition to plant growth
- Ensure interactions remain simple and understandable

## Phase 9 — Environmental Effects

- Make day/night affect plant behavior
- Make day/night affect insect behavior
- Add simple temperature/environment factor if useful
- Add environmental stress
- Add weather variation
- Make environmental conditions influence reproduction
- Make environmental conditions influence mortality

## Phase 10 — Population and Simulation Stability

- Add basic population tracking
- Prevent runaway population growth
- Prevent immediate ecosystem collapse
- Add lightweight spatial lookup/grid if needed
- Remove dead entities efficiently
- Avoid unnecessary per-pixel simulation
- Test larger populations
- Check long-running simulation performance

## Phase 11 — Visual Polish

- Improve plant visuals
- Improve insect visuals
- Improve rocks
- Improve water appearance
- Add subtle environmental effects
- Improve day/night transitions
- Add small visual variation to organisms
- Keep the visual style coherent with procedural palettes

## Phase 12 — User Interface

- Improve debug HUD
- Display population counts
- Display important environmental information
- Add pause/unpause
- Add simulation speed controls
- Add restart/regenerate world
- Show current random seed
- Allow reproducing a simulation using a seed

## Phase 13 — Testing and Cleanup

- Test repeated world generation
- Test repeated simulation runs
- Verify different seeds produce meaningful variation
- Check for entity leaks
- Check for runaway populations
- Check long-running simulation stability
- Check 60 FPS target
- Profile expensive systems
- Remove unnecessary complexity
- Keep modules small and focused
- Document important systems
- Verify clean startup from a fresh checkout

## Phase 14 — Finalization

- Review project architecture
- Remove unused code
- Remove temporary/debug-only code where appropriate
- Finalize configuration values
- Finalize simulation balance
- Final performance pass
- Final visual pass
- Create a reproducible release build/setup
- Update project documentation
- Mark completed project milestones

---

# Rules for Updating This TODO

- Remove completed work.
- Keep unfinished work.
- Keep this file aligned with the actual project state.
- Do not add unnecessary architecture just to satisfy the TODO.
