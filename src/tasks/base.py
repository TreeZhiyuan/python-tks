from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Iterable, List, Optional

import pandas as pd

from src.core.models import TaskRunResult
from src.repositories.base import BaseD1Repository
from src.tushare_client import TushareClientFactory
from src.utils import yesterday


DEFAULT_PAGE_SIZE = 5000


class BaseMoneyflowTask(ABC):
    task_name: str
    page_size: int = DEFAULT_PAGE_SIZE

    def __init__(
        self,
        repository: BaseD1Repository,
        tushare_client_factory: TushareClientFactory | None = None,
    ) -> None:
        self.repository = repository
        self.tushare_client_factory = tushare_client_factory or TushareClientFactory()

    def run(self, trade_date: Optional[date] = None) -> TaskRunResult:
        pro = self.tushare_client_factory.create_pro_client()
        target_date = trade_date or yesterday()
        return self._run_for_date(pro, target_date)

    def run_many(self, trade_dates: Iterable[date]) -> List[TaskRunResult]:
        pro = self.tushare_client_factory.create_pro_client()
        return [self._run_for_date(pro, current_date) for current_date in trade_dates]

    def _run_for_date(self, pro: Any, target_date: date) -> TaskRunResult:
        trade_date_str = target_date.strftime("%Y%m%d")

        frames: List[pd.DataFrame] = []
        offset = 0

        while True:
            df = self.fetch_page(pro, trade_date_str, offset, self.page_size)

            if df is None or df.empty:
                break

            frames.append(df)

            if len(df) < self.page_size:
                break

            offset += self.page_size

        result = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        row_count = len(result.index)
        written_count = self.repository.upsert_rows(result.to_dict(orient="records"))
        return TaskRunResult(
            task_name=self.task_name,
            trade_date=trade_date_str,
            row_count=row_count,
            written_count=written_count,
        )

    @abstractmethod
    def fetch_page(self, pro: Any, trade_date: str, offset: int, limit: int) -> pd.DataFrame:
        raise NotImplementedError
