#!/usr/bin/env python3
"""Terrarium - entry point.   python main.py [--seed N] [--cell-size 4|5] [--selftest TICKS]"""
from __future__ import annotations

import argparse
import dataclasses
import os

from terrarium.config import Config


def main() -> None:
    ap = argparse.ArgumentParser(description="2D terrarium simulation")
    ap.add_argument("--seed", type=int, default=None, help="reproduce a specific terrarium")
    ap.add_argument("--cell-size", type=int, default=None, help="pixels per cell (4 default, 5 = faster)")
    ap.add_argument("--selftest", type=int, default=0, help="headless: run N ticks, print stats, save a PNG")
    args = ap.parse_args()

    cfg = Config()
    if args.cell_size:
        cfg = dataclasses.replace(cfg, window=dataclasses.replace(cfg.window, cell_size=args.cell_size))
    if args.selftest:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    from terrarium.app import App
    app = App(cfg, args.seed)
    if args.selftest:
        import time
        t = time.time()
        for _ in range(args.selftest):
            app.sim.tick()
        dt = time.time() - t
        app.renderer.draw()
        app.hud.draw(app.screen, app)
        app.screenshot()
        print(f"{args.selftest} ticks in {dt:.1f}s ({args.selftest / dt:.0f} ticks/s)")
        print(app.sim.ctx.stats)
        return
    app.run()


if __name__ == "__main__":
    main()
