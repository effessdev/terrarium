import sys
import os

# Ensure repo root on path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.randomizer import Randomizer
from world.world import World
from config import settings


def run_sim(seconds: int = 60):
    rand = Randomizer()
    world = World(settings.WORLD_WIDTH, settings.WORLD_HEIGHT, rand)

    steps = int(settings.SIMULATION_HZ * seconds)
    dt = 1.0 / settings.SIMULATION_HZ

    print(f"Initial worms: {len(world.worms)}")

    min_alive = len([w for w in world.worms if not w.is_dead])

    first_death_reported = False

    for step in range(steps):
        # snapshot alive ids before update
        alive_before = {id(w): w for w in world.worms if not w.is_dead}

        world.update(dt, daylight=1.0)

        # detect newly dead worms and report cause for the first one
        for w in world.worms:
            if id(w) in alive_before and w.is_dead and not first_death_reported:
                reason = None
                if w.starvation_time >= settings.WORM_STARVATION_LIMIT:
                    reason = 'starvation'
                elif w.dehydration_time >= settings.WORM_DEHYDRATION_LIMIT:
                    reason = 'dehydration'
                elif w.age >= (settings.WORM_MIN_LIFESPAN + (settings.WORM_MAX_LIFESPAN - settings.WORM_MIN_LIFESPAN) * w.growth):
                    reason = 'old age'
                else:
                    reason = 'crowding/other'

                print(f"First death at step {step} (sim {step*dt:.1f}s): cause={reason}, age={w.age:.1f}, hunger={w.hunger:.2f}, thirst={w.thirst:.2f}")
                first_death_reported = True

        alive = len([w for w in world.worms if not w.is_dead])
        if alive < min_alive:
            min_alive = alive

        if alive == 0:
            print(f"All worms extinct at step {step} (sim time {step*dt:.1f}s)")
            return

    alive = len([w for w in world.worms if not w.is_dead])
    print(f"After {seconds}s: alive={alive}, total={len(world.worms)}, min_alive={min_alive}")


if __name__ == '__main__':
    run_sim(180)
