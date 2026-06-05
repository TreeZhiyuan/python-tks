from __future__ import annotations

from datetime import date, timedelta


def yesterday() -> date:
    return date.today() - timedelta(days=1)
