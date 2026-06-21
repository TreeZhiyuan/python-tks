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
