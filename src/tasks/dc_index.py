from __future__ import annotations

from datetime import date
from typing import Any, Iterable

import pandas as pd

from src.core.models import TaskRunResult
from src.db.client import DatabaseClient, build_database_client
from src.repositories.dc_index_repository import DcIndexRepository
from src.tushare_client import TushareClientFactory
from src.utils import china_today


DC_INDEX_FIELDS = ",".join(
    [
        "ts_code",
        "trade_date",
        "name",
        "leading",
        "leading_code",
        "pct_change",
        "leading_pct",
        "total_mv",
        "turnover_rate",
        "up_num",
        "down_num",
        "idx_type",
        "level",
    ]
)
DEFAULT_IDX_TYPE = "概念板块"


class DcIndexTask:
    task_name = "dc_index"

    def __init__(
        self,
        repository: DcIndexRepository | None = None,
        db_client: DatabaseClient | None = None,
        tushare_client_factory: TushareClientFactory | None = None,
    ) -> None:
        self.repository = repository or DcIndexRepository(db_client or build_database_client())
        self.tushare_client_factory = tushare_client_factory or TushareClientFactory()

    def run(
        self,
        trade_date: date | str | None = None,
        ts_code: str | None = None,
        name: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        idx_type: str = DEFAULT_IDX_TYPE,
    ) -> TaskRunResult:
        target_trade_date = self.resolve_trade_date(trade_date)
        pro = self.tushare_client_factory.create_pro_client()
        df = self.fetch(
            pro,
            trade_date=target_trade_date,
            ts_code=ts_code,
            name=name,
            start_date=start_date,
            end_date=end_date,
            idx_type=idx_type,
        )
        result = df if df is not None else pd.DataFrame()
        rows = result.to_dict(orient="records")
        written_count = self.repository.upsert_rows(rows)
        return TaskRunResult(
            task_name=self.task_name,
            trade_date=target_trade_date,
            row_count=len(rows),
            written_count=written_count,
        )

    def run_many(self, trade_dates: Iterable[date | str]) -> list[TaskRunResult]:
        return [self.run(trade_date=current_date) for current_date in trade_dates]

    def fetch(
        self,
        pro: Any,
        trade_date: str,
        ts_code: str | None = None,
        name: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        idx_type: str = DEFAULT_IDX_TYPE,
    ) -> pd.DataFrame:
        params: dict[str, Any] = {
            "trade_date": trade_date,
            "idx_type": idx_type,
            "fields": DC_INDEX_FIELDS,
        }
        if ts_code:
            params["ts_code"] = ts_code
        if name:
            params["name"] = name
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return pro.dc_index(**params)

    def resolve_trade_date(self, trade_date: date | str | None) -> str:
        if trade_date is None:
            return china_today().strftime("%Y%m%d")
        if isinstance(trade_date, date):
            return trade_date.strftime("%Y%m%d")
        return trade_date.replace("-", "")
