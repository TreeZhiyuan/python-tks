from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Iterable, List, Sequence

from src.db.d1 import D1Client


@dataclass
class BaseD1Repository(ABC):
    d1_client: D1Client

    @property
    @abstractmethod
    def table_name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def select_columns(self) -> Sequence[str]:
        raise NotImplementedError

    @property
    @abstractmethod
    def source_to_db_field_map(self) -> Sequence[tuple[str, str]]:
        raise NotImplementedError

    @property
    def key_columns(self) -> Sequence[str]:
        return ("trade_date", "ts_code")

    def upsert_rows(self, rows: Iterable[dict[str, Any]]) -> int:
        payload: List[list[Any]] = []

        for row in rows:
            payload.append(
                [row.get(source_field) for source_field, _ in self.source_to_db_field_map]
            )

        if not payload:
            return 0

        self.d1_client.executemany(self.build_upsert_sql(), payload)
        return len(payload)

    def upsert_rows_in_batches(
        self,
        rows: Iterable[dict[str, Any]],
        batch_size: int = 100,
    ) -> int:
        total_count = 0
        batch: List[dict[str, Any]] = []

        for row in rows:
            batch.append(row)
            if len(batch) >= batch_size:
                total_count += self.upsert_rows(batch)
                batch = []

        if batch:
            total_count += self.upsert_rows(batch)

        return total_count

    def find_by_trade_date(self, trade_date: str) -> list[dict[str, Any]]:
        sql = self.build_select_by_trade_date_sql()
        return self.d1_client.fetch_all(sql, [trade_date])

    def build_upsert_sql(self) -> str:
        db_columns = [target_field for _, target_field in self.source_to_db_field_map]
        placeholders = ", ".join(["?"] * len(db_columns))
        column_sql = ",\n    ".join(db_columns)
        return f"""
INSERT OR REPLACE INTO {self.table_name} (
    {column_sql}
) VALUES ({placeholders})
"""

    def build_select_by_trade_date_sql(self) -> str:
        column_sql = ",\n    ".join(self.select_columns)
        return f"""
SELECT
    {column_sql}
FROM {self.table_name}
WHERE trade_date = ?
ORDER BY ts_code
"""
