from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Iterable, List, Optional

import pandas as pd
import tushare as ts

from src.config import TUSHARE_TOKEN
from src.db.d1 import D1Client
from src.repositories.moneyflow_cnt_ths_repository import MoneyflowCntThsRepository
from src.utils import yesterday


MAX_LIMIT = 5000


@dataclass
class MoneyflowCntThsResult:
    trade_date: str
    written_count: int
    row_count: int


@dataclass
class MoneyflowCntThsTask:
    token: str = TUSHARE_TOKEN
    repository: MoneyflowCntThsRepository | None = None

    def run(self, trade_date: Optional[date] = None) -> MoneyflowCntThsResult:
        pro = self._create_client()
        target_date = trade_date or yesterday()
        return self._run_for_date(pro, target_date)

    def run_many(self, trade_dates: Iterable[date]) -> List[MoneyflowCntThsResult]:
        pro = self._create_client()
        return [self._run_for_date(pro, current_date) for current_date in trade_dates]

    def _create_client(self) -> Any:
        if not self.token or self.token == "REPLACE_WITH_YOUR_TUSHARE_TOKEN":
            raise ValueError("TUSHARE_TOKEN is not configured. Please update your .env file.")

        ts.set_token(self.token)
        return ts.pro_api()

    def _run_for_date(self, pro: Any, target_date: date) -> MoneyflowCntThsResult:
        trade_date_str = target_date.strftime("%Y%m%d")

        frames: List[pd.DataFrame] = []
        offset = 0

        while True:
            df = pro.moneyflow_cnt_ths(
                trade_date=trade_date_str,
                limit=MAX_LIMIT,
                offset=offset,
            )

            if df is None or df.empty:
                break

            frames.append(df)

            if len(df) < MAX_LIMIT:
                break

            offset += MAX_LIMIT

        result = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        row_count = len(result.index)
        repository = self.repository or MoneyflowCntThsRepository(D1Client())
        written_count = repository.upsert_rows(result.to_dict(orient="records"))
        return MoneyflowCntThsResult(
            trade_date=trade_date_str,
            written_count=written_count,
            row_count=row_count,
        )
