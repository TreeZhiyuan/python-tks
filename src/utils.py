from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo


CHINA_TIMEZONE = ZoneInfo("Asia/Shanghai")


def china_today() -> date:
    return datetime.now(CHINA_TIMEZONE).date()


def yesterday() -> date:
    return china_today() - timedelta(days=1)


def previous_china_workday(reference_date: date | None = None) -> date:
    target_date = (reference_date or china_today()) - timedelta(days=1)
    while target_date.weekday() >= 5:
        target_date -= timedelta(days=1)
    return target_date


def one_year_ago(reference_date: date | None = None) -> date:
    current_date = reference_date or china_today()
    try:
        return current_date.replace(year=current_date.year - 1)
    except ValueError:
        return current_date.replace(year=current_date.year - 1, day=28)
