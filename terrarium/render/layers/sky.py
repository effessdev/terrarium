"""Sky gradient, stars, sun and moon."""
from __future__ import annotations

import math

import numpy as np

from ..common import blend3
from .base import RenderLayer


class SkyLayer(RenderLayer):
    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        g = ctx.grid
        rng = ctx.rng.child("stars").np
        n = ctx.config.render.star_count
        self.sx = rng.integers(2, g.w - 2, n)
        self.sy = rng.integers(2, int(g.h * 0.55), n)
        self.sb = rng.uniform(0.4, 1.0, n).astype(np.float32)
        self.sp = rng.uniform(0, 6.28, n).astype(np.float32)

    def draw(self, st) -> None:
        ctx = self.ctx
        pal, clock = ctx.palette, ctx.clock
        g = ctx.grid
        d, n, t, morning = clock.phase_weights()
        twi = pal.sky_dawn if morning else pal.sky_dusk
        top = np.array(blend3(d, n, t, pal.sky_day[0], pal.sky_night[0], twi[0]), np.float32)
        bot = np.array(blend3(d, n, t, pal.sky_day[1], pal.sky_night[1], twi[1]), np.float32)
        ramp = np.clip(np.arange(g.h, dtype=np.float32) / (g.h * 0.72), 0, 1)[:, None]
        grad = top + (bot - top) * ramp
        st.frame[:] = grad[:, None, :].astype(np.uint8)
        st.sky_bottom = tuple(int(v) for v in bot)
        if n > 0.02:
            tw = 0.65 + 0.35 * np.sin(self.sp + st.time * 2.0)
            k = (n * self.sb * tw)[:, None]
            base = st.frame[self.sy, self.sx].astype(np.float32)
            star = np.array(pal.star, np.float32)
            st.frame[self.sy, self.sx] = (base + (star - base) * k).astype(np.uint8)
        if clock.sun_height > -0.1:
            self._disc(st, clock.sun_u, pal.sun, 6, 1.0)
        if 0.0 <= clock.moon_u <= 1.0 and clock.sun_height < 0.15:
            self._disc(st, clock.moon_u, pal.moon, 4, 0.9)

    def _disc(self, st, u, color, r, k) -> None:
        g = self.ctx.grid
        cx = g.w * (0.08 + 0.84 * u)
        cy = g.h * 0.64 - math.sin(math.pi * min(1.0, max(0.0, u))) * g.h * 0.52
        x0, x1 = int(max(0, cx - r * 3)), int(min(g.w, cx + r * 3 + 1))
        y0, y1 = int(max(0, cy - r * 3)), int(min(g.h, cy + r * 3 + 1))
        if x1 <= x0 or y1 <= y0:
            return
        yy, xx = np.mgrid[y0:y1, x0:x1]
        dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        core = np.clip((r + 0.7 - dist), 0, 1)
        glow = np.clip(1.0 - dist / (r * 3), 0, 1) ** 2 * 0.35
        a = np.clip(core + glow, 0, 1)[..., None] * k
        reg = st.frame[y0:y1, x0:x1].astype(np.float32)
        st.frame[y0:y1, x0:x1] = (reg + (np.array(color, np.float32) - reg) * a).astype(np.uint8)
