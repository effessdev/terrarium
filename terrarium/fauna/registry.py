"""Insect species registry with automatic discovery (see ``flora/registry.py``)."""
from __future__ import annotations

import importlib
import pkgutil

_SPECIES: dict = {}
_LOADED = False


def register(cls):
    inst = cls()
    _SPECIES[inst.name] = inst
    return cls


def _load() -> None:
    global _LOADED
    if _LOADED:
        return
    _LOADED = True
    from . import species as pkg

    modules = list(pkgutil.iter_modules(pkg.__path__))
    if modules:
        for m in modules:
            importlib.import_module(f"{pkg.__name__}.{m.name}")
    else:
        # PyInstaller fallback: explicitly import known species modules
        from .species import ant, beetle, butterfly, firefly


def all_species() -> list:
    _load()
    return list(_SPECIES.values())


def get_species(name: str):
    _load()
    return _SPECIES[name]
