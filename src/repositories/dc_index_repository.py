from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from src.db.client import DatabaseClient
from src.repositories.base import BaseD1Repository


@dataclass
class DcIndexRepository(BaseD1Repository):
    db_client: DatabaseClient

    @property
    def table_name(self) -> str:
        return "dc_index"

    @property
    def select_columns(self) -> Sequence[str]:
        return (
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
        )

    @property
    def source_to_db_field_map(self) -> Sequence[tuple[str, str]]:
        return (
            ("ts_code", "ts_code"),
            ("trade_date", "trade_date"),
            ("name", "name"),
            ("leading", "leading"),
            ("leading_code", "leading_code"),
            ("pct_change", "pct_change"),
            ("leading_pct", "leading_pct"),
            ("total_mv", "total_mv"),
            ("turnover_rate", "turnover_rate"),
            ("up_num", "up_num"),
            ("down_num", "down_num"),
            ("idx_type", "idx_type"),
            ("level", "level"),
        )

