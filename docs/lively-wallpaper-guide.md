# Turning Terrarium into a Windows Live Wallpaper (via Lively)

This project can be run as an animated desktop wallpaper using
[Lively Wallpaper](https://github.com/rocksdanister/lively) — a free, open-source
(GPLv3) live-wallpaper app. Lively handles all the hard parts: embedding the
window behind the desktop icons, Explorer crashes/restarts, multi-monitor, and
startup on login.

> **Important:** use the **installer version** of Lively (from
> https://www.rocksdanister.com/lively/ or `winget install rocksdanister.Lively`).
> The **Microsoft Store version does NOT support Application (.exe) wallpapers.**

---

## Step 1 — Build the EXE

```powershell
pip install pyinstaller ; pyinstaller Terrarium.spec
```

Output: `dist\Terrarium\Terrarium.exe` (one-dir build, keep the whole folder).

Recommended before building — wallpaper-friendly tweaks in `terrarium/config.py`
(or a small `--wallpaper` preset later):

- `render.show_hud = False`
- Lower `window.fps_cap` (e.g. 30) and start at a low speed index to save CPU.

## Step 2 — Create the wallpaper package

Lively's import wizard can choke on apps that resize themselves, so build the
project file **manually** and ship it as a `.zip` (this is the officially
recommended workaround):

```
terrarium-wallpaper/
├── LivelyInfo.json          <- must be at the root
└── Terrarium/               <- entire dist folder from Step 1
    ├── Terrarium.exe
    └── _internal/...
```

`LivelyInfo.json`:

```json
{
  "AppVersion": "1.0.0.0",
  "Title": "Terrarium",
  "Thumbnail": "preview.jpg",
  "Preview": null,
  "Desc": "A living 2D terrarium: plants grow, insects roam, rain falls.",
  "Author": "YOUR_NAME",
  "License": "MIT",
  "Contact": "https://github.com/YOUR_USER/terrarium",
  "Type": 0,
  "FileName": "Terrarium/Terrarium.exe",
  "Arguments": null,
  "IsAbsolutePath": false
}
```

- `Type: 0` = Application wallpaper.
- `IsAbsolutePath: false` means `FileName` is relative to the package root.
- `Thumbnail` is optional (shown in Lively's library); the file, if set, must
  also live inside the package.

Zip it so that `LivelyInfo.json` sits at the **root of the archive**:

```powershell
Compress-Archive -Path terrarium-wallpaper\* -DestinationPath terrarium-wallpaper.zip
```

## Step 3 — Install as wallpaper

**Manual (first time):** open Lively → drag `terrarium-wallpaper.zip` onto the
library grid → select it → Apply. Done — it now starts with Windows
automatically.

**One click for your users:** Lively ships a command utility (`Livelycu.exe`)
that can apply a wallpaper project from the CLI:

```powershell
Livelycu.exe setwp --file "C:\path\to\terrarium-wallpaper.zip"
```

So your app/installer can:

1. Detect Lively (check `%LOCALAPPDATA%\Programs\Lively\Lively.exe` or the
   Start-Menu shortcut; if missing, prompt the user with a one-line
   `winget install rocksdanister.Lively` button).
2. Call `setwp --file ...` on first launch. From then on Lively keeps the
   terrarium alive across reboots.

## Step 4 (optional) — World continuity across restarts

Right now every launch generates a fresh world. Because the simulation is
fully deterministic from its seed, you can make reboots *continue* the same
terrarium instead of restarting it:

1. Persist `{"seed": ctx.rng.seed, "ticks": <tick_count>}` to
   `%APPDATA%\Terrarium\session.json` (write every N ticks and on exit).
2. On startup, if a session file exists, call `App.new_world(seed)` and
   fast-forward `ticks` simulation ticks (cap catch-up, e.g. 200k ticks, so a
   long absence doesn't delay boot).
3. Keep `--seed` as an override for a fresh world, plus a "New World" action
   that deletes the session file.

Lively itself cannot do this for you — the state must live inside your EXE.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Import wizard hangs / shows black preview | Use the manual `.zip` method above (skips the preview capture). |
| Wallpaper shows a normal floating window, not embedded | You're using the Store version — switch to the installer version. |
| High CPU on battery | Lower `fps_cap` / sim speed in `config.py`; repackage. |
| Lively resizes the window oddly | Don't change window size at runtime; let Lively own sizing (per Lively's app-wallpaper notes). |
| User has no Lively and you can't ship it | Fallback: embed via the Win32 WorkerW technique inside your own EXE (~100 lines of ctypes, more edge cases to maintain). |

## Notes on licensing & distribution

- Lively is GPLv3 and freely downloadable — point users to it, but don't bake
  its installer into your package (distribution terms); one
  `winget`/download click is the normal flow.
- Wallpaper Engine also supports EXE wallpapers, but it is paid software and
  cannot be bundled — only your wallpaper package (folder with
  `project.json`, `Type: "application"`) can be distributed via Steam Workshop.
