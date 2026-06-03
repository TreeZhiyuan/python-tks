from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path


def yesterday() -> date:
    return date.today() - timedelta(days=1)


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path

