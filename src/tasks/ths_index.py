from __future__ import annotations

from typing import Any, Iterable

import pandas as pd

from src.core.models import TaskRunResult
from src.db.client import DatabaseClient, build_database_client
from src.repositories.ths_index_repository import ThsIndexRepository
from src.tushare_client import TushareClientFactory


THS_INDEX_FIELDS = ",".join(
    [
        "ts_code",
        "name",
        "count",
        "exchange",
        "list_date",
        "type",
    ]
)


class ThsIndexTask:
    task_name = "ths_index"

    def __init__(
        self,
        repository: ThsIndexRepository | None = None,
        db_client: DatabaseClient | None = None,
        tushare_client_factory: TushareClientFactory | None = None,
    ) -> None:
        self.repository = repository or ThsIndexRepository(db_client or build_database_client())
        self.tushare_client_factory = tushare_client_factory or TushareClientFactory()

    def run(
        self,
        ts_code: str | None = None,
        exchange: str | None = None,
        type_: str | None = None,
    ) -> TaskRunResult:
        pro = self.tushare_client_factory.create_pro_client()
        df = self.fetch(
            pro,
            ts_code=ts_code,
            exchange=exchange,
            type_=type_,
        )
        result = df if df is not None else pd.DataFrame()
        rows = result.to_dict(orient="records")
        written_count = self.repository.upsert_rows(rows)
        return TaskRunResult(
            task_name=self.task_name,
            trade_date=None,
            row_count=len(rows),
            written_count=written_count,
        )

    def run_many(self, trade_dates: Iterable[Any]) -> list[TaskRunResult]:
        return [self.run()]

    def fetch(
        self,
        pro: Any,
        ts_code: str | None = None,
        exchange: str | None = None,
        type_: str | None = None,
    ) -> pd.DataFrame:
        params: dict[str, Any] = {"fields": THS_INDEX_FIELDS}
        if ts_code:
            params["ts_code"] = ts_code
        if exchange:
            params["exchange"] = exchange
        if type_:
            params["type"] = type_
        return pro.ths_index(**params)
