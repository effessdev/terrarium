"""Long-run ecosystem check:  python tools/stability.py SEED [DAYS]  (headless)."""
import os, sys, collections
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from terrarium.builder import build_simulation
from terrarium.world.materials import WATER

seed = int(sys.argv[1]); days = int(sys.argv[2]) if len(sys.argv) > 2 else 4
sim = build_simulation(seed=seed); ctx = sim.ctx
causes = collections.Counter()
ctx.bus.subscribe("plant_died", lambda plant, cause: causes.update([cause]))
row = []
for i in range(int(days * ctx.config.time.day_length * ctx.config.time.tick_rate) + 1):
    if i % 3600 == 0:
        s = ctx.stats
        row.append(f"d{ctx.clock.day}: W{int((ctx.grid.mat == WATER).sum())} P{s['plant_total']} I{s['insect_total']}")
    sim.tick()
s = ctx.stats
print(seed, ctx.palette.name, ctx.params.describe, "|", " | ".join(row))
print("   plants", s["plants"]); print("   insects", s["insects"], "rescues", s["rescues"]); print("   deaths", dict(causes))
