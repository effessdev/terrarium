"""Mist: visualises the vapour field over the open air."""
from __future__ import annotations

import numpy as np

from ...palette.color_utils import lerp
from .base import RenderLayer


class FogLayer(RenderLayer):
    def draw(self, st) -> None:
        ctx = self.ctx
        vap = ctx.vapor
        hum = vap.humidity(ctx.weather.temperature)
        a = np.clip((hum - 0.30) * 0.75, 0.0, 0.85) * ctx.config.render.fog_strength
        if a.max() < 0.02:
            return
        b = vap.BLOCK
        g = ctx.grid
        big = np.repeat(np.repeat(a, b, axis=0), b, axis=1)[:g.h, :g.w]
        big = (big + np.roll(big, b // 2, 0) + np.roll(big, -b // 2, 1) + np.roll(big, (b // 2, -b // 2), (0, 1))) * 0.25
        big = big * st.sky_mask
        fog = np.array(lerp(st.sky_bottom, (255, 255, 255), 0.55), np.float32)
        f = st.frame.astype(np.float32)
        st.frame[:] = (f + (fog - f) * big[..., None]).astype(np.uint8)
