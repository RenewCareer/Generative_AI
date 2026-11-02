"""Helpers for the per-module test suites."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


def load_lesson(path: str | Path) -> ModuleType:
    """Import a lesson file. Their names start with digits, so ``import`` cannot do it."""
    path = Path(path)
    spec = importlib.util.spec_from_file_location(f"lesson_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
