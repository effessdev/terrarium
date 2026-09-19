"""Simulation timing."""

from __future__ import annotations

import time


class SimulationClock:
    """Keeps simulation time independent from rendering FPS."""

    def __init__(self, simulation_hz: int) -> None:
        if simulation_hz <= 0:
            raise ValueError("simulation_hz must be greater than zero")

        self.simulation_hz = simulation_hz
        self.fixed_dt = 1.0 / simulation_hz

        self.accumulator = 0.0
        self.total_simulation_time = 0.0

        self._last_time = time.perf_counter()

    def tick(self) -> float:
        """
        Add elapsed real time to the simulation accumulator.

        Returns the elapsed real-world time since the previous call.
        """
        current_time = time.perf_counter()
        elapsed = current_time - self._last_time
        self._last_time = current_time

        # Prevent a debugger pause/window freeze from causing a huge
        # simulation jump when execution resumes.
        elapsed = min(elapsed, 0.25)

        self.accumulator += elapsed
        return elapsed

    def should_step(self) -> bool:
        """Return True when another fixed simulation step is ready."""
        return self.accumulator >= self.fixed_dt

    def consume_step(self) -> None:
        """Consume one fixed simulation step."""
        self.accumulator -= self.fixed_dt
        self.total_simulation_time += self.fixed_dt
