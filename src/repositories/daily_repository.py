from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from src.db.client import DatabaseClient
from src.repositories.base import BaseD1Repository


@dataclass
class DailyRepository(BaseD1Repository):
    db_client: DatabaseClient

    @property
    def table_name(self) -> str:
        return "daily"

    @property
    def select_columns(self) -> Sequence[str]:
        return (
            "ts_code",
            "trade_date",
            "open_price",
            "high_price",
            "low_price",
            "close_price",
            "pre_close",
            "change_amount",
            "pct_chg",
            "vol",
            "amount",
        )

    @property
    def source_to_db_field_map(self) -> Sequence[tuple[str, str]]:
        return (
            ("ts_code", "ts_code"),
            ("trade_date", "trade_date"),
            ("open", "open_price"),
            ("high", "high_price"),
            ("low", "low_price"),
            ("close", "close_price"),
            ("pre_close", "pre_close"),
            ("change", "change_amount"),
            ("pct_chg", "pct_chg"),
            ("vol", "vol"),
            ("amount", "amount"),
        )

    def delete_older_than_trade_date(self, cutoff_trade_date: str) -> None:
        self.db_client.execute(
            """
DELETE FROM daily
WHERE trade_date < ?
""",
            [cutoff_trade_date],
        )

    def find_recent_by_ts_codes(
        self,
        ts_codes: Sequence[str],
        limit_per_code: int,
        end_trade_date: str | None = None,
        batch_size: int = 500,
    ) -> list[dict]:
        if limit_per_code <= 0 or not ts_codes:
            return []

        rows: list[dict] = []
        column_sql = ",\n        ".join(self.select_columns)
        outer_column_sql = ",\n    ".join(self.select_columns)

        for start in range(0, len(ts_codes), batch_size):
            batch = list(ts_codes[start : start + batch_size])
            placeholders = ", ".join(["?"] * len(batch))
            where_parts = [f"ts_code IN ({placeholders})"]
            params: list[str | int] = [*batch]

            if end_trade_date:
                where_parts.append("trade_date <= ?")
                params.append(end_trade_date)

            params.append(limit_per_code)
            where_sql = "\n      AND ".join(where_parts)
            rows.extend(
                self.db_client.fetch_all(
                    f"""
SELECT
    {outer_column_sql}
FROM (
    SELECT
        {column_sql},
        ROW_NUMBER() OVER (
            PARTITION BY ts_code
            ORDER BY trade_date DESC
        ) AS row_number
    FROM daily
    WHERE {where_sql}
)
WHERE row_number <= ?
ORDER BY ts_code, trade_date
""",
                    params,
                )
            )

        return rows
