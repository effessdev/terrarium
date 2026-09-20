"""Minimal publish/subscribe bus so systems can talk without importing each other.

Well-known events (add yours here so everybody can find them):
    dawn, dusk                      -- emitted by ``DayClock``
    new_day(day)                    -- emitted by ``DayClock``
    plant_died(plant, cause)        -- emitted by ``Plant.die``
    insect_died(insect, cause)      -- emitted by ``Insect.die``
    pollinated(plant)               -- emitted by nectar feeding
"""
from __future__ import annotations

from collections import defaultdict
from typing import Callable


class EventBus:
    def __init__(self) -> None:
        self._subs: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, name: str, fn: Callable) -> None:
        self._subs[name].append(fn)

    def emit(self, name: str, **payload) -> None:
        for fn in self._subs.get(name, ()):
            fn(**payload)
