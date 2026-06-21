from __future__ import annotations

from typing import Any

import pandas as pd

from src.db.client import DatabaseClient, build_database_client
from src.repositories.moneyflow_repository import MoneyflowRepository
from src.tasks.base import BaseMoneyflowTask


class MoneyflowTask(BaseMoneyflowTask):
    task_name = "moneyflow"

    def __init__(self, db_client: DatabaseClient | None = None) -> None:
        super().__init__(repository=MoneyflowRepository(db_client or build_database_client()))

    def fetch_page(self, pro: Any, trade_date: str, offset: int, limit: int) -> pd.DataFrame:
        return pro.moneyflow(
            trade_date=trade_date,
            limit=limit,
            offset=offset,
        )
