from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.core.models import TaskRunResult
from src.storage.json_store import JsonSnapshotStore
from src.tushare_client import TushareClientFactory


STOCK_BASIC_FIELDS = ",".join(
    [
        "ts_code",
        "symbol",
        "name",
        "area",
        "industry",
        "fullname",
        "enname",
        "cnspell",
        "market",
        "exchange",
        "curr_type",
        "list_status",
        "list_date",
        "delist_date",
        "is_hs",
        "act_name",
        "act_ent_type",
    ]
)


class StockBasicTask:
    task_name = "stock_basic"

    def __init__(
        self,
        snapshot_store: JsonSnapshotStore | None = None,
        tushare_client_factory: TushareClientFactory | None = None,
    ) -> None:
        self.snapshot_store = snapshot_store or JsonSnapshotStore(Path("data/stock_basic"))
        self.tushare_client_factory = tushare_client_factory or TushareClientFactory()

    def run(self, trade_date: Any = None) -> TaskRunResult:
        pro = self.tushare_client_factory.create_pro_client()
        df = self.fetch(pro)
        result = df if df is not None else pd.DataFrame()
        rows = result.to_dict(orient="records")
        output_file = self.snapshot_store.write_snapshot(self.task_name, rows)
        return TaskRunResult(
            task_name=self.task_name,
            trade_date=None,
            row_count=len(rows),
            written_count=len(rows),
            output_path=str(output_file),
        )

    def run_many(self, trade_dates: Any) -> list[TaskRunResult]:
        return [self.run()]

    def fetch(self, pro: Any) -> pd.DataFrame:
        frames: list[pd.DataFrame] = []
        for list_status in ("L", "D", "P"):
            df = pro.stock_basic(
                exchange="",
                list_status=list_status,
                fields=STOCK_BASIC_FIELDS,
            )
            if df is not None and not df.empty:
                frames.append(df)

        if not frames:
            return pd.DataFrame()

        result = pd.concat(frames, ignore_index=True)
        return result.drop_duplicates(subset=["ts_code"], keep="last")
