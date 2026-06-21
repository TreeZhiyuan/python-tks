from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, Iterable, List, Optional

import pandas as pd

from src.core.models import TaskRunResult
from src.db.client import DatabaseClient, build_database_client
from src.repositories.daily_repository import DailyRepository
from src.storage.json_store import JsonSnapshotStore
from src.tushare_client import TushareClientFactory
from src.utils import one_year_ago, yesterday


class DailyTask:
    task_name = "daily"
    stock_code_batch_size = 500
    write_batch_size = 100

    def __init__(
        self,
        repository: DailyRepository | None = None,
        db_client: DatabaseClient | None = None,
        snapshot_store: JsonSnapshotStore | None = None,
        tushare_client_factory: TushareClientFactory | None = None,
    ) -> None:
        self.repository = repository or DailyRepository(db_client or build_database_client())
        self.snapshot_store = snapshot_store or JsonSnapshotStore(Path("data/stock_basic"))
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
        stock_codes = self.load_stock_codes()
        rows: List[dict[str, Any]] = []

        for stock_code_batch in self.iter_stock_code_batches(stock_codes):
            df = self.fetch_daily_for_stock_batch(pro, stock_code_batch, trade_date_str)
            if df is None or df.empty:
                continue
            rows.extend(df.to_dict(orient="records"))

        written_count = self.repository.upsert_rows_in_batches(
            rows,
            batch_size=self.write_batch_size,
        )
        self.delete_expired_rows()
        return TaskRunResult(
            task_name=self.task_name,
            trade_date=trade_date_str,
            row_count=len(rows),
            written_count=written_count,
        )

    def load_stock_codes(self) -> list[str]:
        try:
            snapshot = self.snapshot_store.read_snapshot("stock_basic")
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                "stock_basic snapshot not found. Run `python -m src.main --tasks stock_basic` first."
            ) from exc

        stock_codes = [
            str(row["ts_code"]).strip()
            for row in snapshot.get("rows", [])
            if row.get("ts_code")
        ]
        return list(dict.fromkeys(stock_codes))

    def iter_stock_code_batches(self, stock_codes: list[str]) -> Iterable[list[str]]:
        for start_index in range(0, len(stock_codes), self.stock_code_batch_size):
            yield stock_codes[start_index : start_index + self.stock_code_batch_size]

    def fetch_daily_for_stock_batch(
        self,
        pro: Any,
        stock_codes: list[str],
        trade_date: str,
    ) -> pd.DataFrame:
        return pro.daily(
            ts_code=",".join(stock_codes),
            trade_date=trade_date,
        )

    def delete_expired_rows(self) -> None:
        cutoff_trade_date = one_year_ago().strftime("%Y%m%d")
        self.repository.delete_older_than_trade_date(cutoff_trade_date)
