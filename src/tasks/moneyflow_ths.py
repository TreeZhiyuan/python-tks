from __future__ import annotations

from typing import Any

import pandas as pd

from src.db.d1 import D1Client
from src.repositories.moneyflow_ths_repository import MoneyflowThsRepository
from src.tasks.base import BaseMoneyflowTask


class MoneyflowThsTask(BaseMoneyflowTask):
    task_name = "moneyflow_ths"

    def __init__(self) -> None:
        super().__init__(repository=MoneyflowThsRepository(D1Client()))

    def fetch_page(self, pro: Any, trade_date: str, offset: int, limit: int) -> pd.DataFrame:
        return pro.moneyflow_ths(
            trade_date=trade_date,
            limit=limit,
            offset=offset,
        )
