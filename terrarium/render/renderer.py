"""Renderer: runs the low-resolution layer stack, scales it up, adds overlays."""
from __future__ import annotations

import numpy as np
import pygame

from .common import RenderState
from .layers.flora import FloraLayer
from .layers.fog import FogLayer
from .layers.lighting import LightingLayer
from .layers.sky import SkyLayer
from .layers.terrain import TerrainLayer
from .overlays import EntityOverlay, GlassOverlay


class Renderer:
    def __init__(self, ctx, screen) -> None:
        self.ctx = ctx
        self.screen = screen
        g = ctx.grid
        ctx.render_shade_lut = (0.42 + 0.58 * np.exp(-np.arange(256) / 40.0)).astype(np.float32)
        self.state = RenderState(g.w, g.h)
        # order matters: sky -> terrain -> plants -> mist -> lighting
        self.layers = [SkyLayer(ctx), TerrainLayer(ctx), FloraLayer(ctx), FogLayer(ctx), LightingLayer(ctx)]
        size = screen.get_size()
        self.overlays = [EntityOverlay(ctx), GlassOverlay(ctx, size)]
        self._size = size

    def draw(self) -> None:
        st = self.state
        st.time = self.ctx.time
        for layer in self.layers:
            layer.draw(st)
        g = self.ctx.grid
        small = pygame.image.frombuffer(np.ascontiguousarray(st.frame), (g.w, g.h), "RGB")
        pygame.transform.scale(small, self._size, self.screen) if small.get_bitsize() == self.screen.get_bitsize() \
            else self.screen.blit(pygame.transform.scale(small, self._size), (0, 0))
        for ov in self.overlays:
            ov.draw(self.screen)
