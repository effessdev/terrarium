"""Render layer interface: mutate ``state.frame`` (H, W, 3 uint8, low resolution)."""
from __future__ import annotations


class RenderLayer:
    def __init__(self, ctx) -> None:
        self.ctx = ctx

    def draw(self, state) -> None:  # pragma: no cover - interface
        raise NotImplementedError
