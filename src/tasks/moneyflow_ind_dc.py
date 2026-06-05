from __future__ import annotations

from typing import Any

import pandas as pd

from src.db.d1 import D1Client
from src.repositories.moneyflow_ind_dc_repository import MoneyflowIndDcRepository
from src.tasks.base import BaseMoneyflowTask


class MoneyflowIndDcTask(BaseMoneyflowTask):
    task_name = "moneyflow_ind_dc"

    def __init__(self) -> None:
        super().__init__(repository=MoneyflowIndDcRepository(D1Client()))

    def fetch_page(self, pro: Any, trade_date: str, offset: int, limit: int) -> pd.DataFrame:
        return pro.moneyflow_ind_dc(
            trade_date=trade_date,
            limit=limit,
            offset=offset,
        )
