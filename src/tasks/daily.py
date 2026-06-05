from __future__ import annotations

from typing import Any

import pandas as pd

from src.db.d1 import D1Client
from src.repositories.daily_repository import DailyRepository
from src.tasks.base import BaseMoneyflowTask


class DailyTask(BaseMoneyflowTask):
    task_name = "daily"
    page_size = 6000

    def __init__(self) -> None:
        super().__init__(repository=DailyRepository(D1Client()))

    def fetch_page(self, pro: Any, trade_date: str, offset: int, limit: int) -> pd.DataFrame:
        return pro.daily(
            trade_date=trade_date,
            limit=limit,
            offset=offset,
        )
