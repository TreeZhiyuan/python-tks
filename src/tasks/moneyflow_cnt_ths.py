from __future__ import annotations

from typing import Any

import pandas as pd

from src.db.client import DatabaseClient, build_database_client
from src.repositories.moneyflow_cnt_ths_repository import MoneyflowCntThsRepository
from src.tasks.base import BaseMoneyflowTask


class MoneyflowCntThsTask(BaseMoneyflowTask):
    task_name = "moneyflow_cnt_ths"

    def __init__(self, db_client: DatabaseClient | None = None) -> None:
        super().__init__(repository=MoneyflowCntThsRepository(db_client or build_database_client()))

    def fetch_page(self, pro: Any, trade_date: str, offset: int, limit: int) -> pd.DataFrame:
        return pro.moneyflow_cnt_ths(
            trade_date=trade_date,
            limit=limit,
            offset=offset,
        )
