from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from src.db.client import DatabaseClient
from src.repositories.base import BaseD1Repository


@dataclass
class MoneyflowThsRepository(BaseD1Repository):
    db_client: DatabaseClient

    @property
    def table_name(self) -> str:
        return "moneyflow_ths"

    @property
    def select_columns(self) -> Sequence[str]:
        return (
            "trade_date",
            "ts_code",
            "name",
            "pct_change",
            "latest_price",
            "net_amount",
            "net_d5_amount",
            "buy_lg_amount",
            "buy_lg_amount_rate",
            "buy_md_amount",
            "buy_md_amount_rate",
            "buy_sm_amount",
            "buy_sm_amount_rate",
        )

    @property
    def source_to_db_field_map(self) -> Sequence[tuple[str, str]]:
        return (
            ("trade_date", "trade_date"),
            ("ts_code", "ts_code"),
            ("name", "name"),
            ("pct_change", "pct_change"),
            ("latest", "latest_price"),
            ("net_amount", "net_amount"),
            ("net_d5_amount", "net_d5_amount"),
            ("buy_lg_amount", "buy_lg_amount"),
            ("buy_lg_amount_rate", "buy_lg_amount_rate"),
            ("buy_md_amount", "buy_md_amount"),
            ("buy_md_amount_rate", "buy_md_amount_rate"),
            ("buy_sm_amount", "buy_sm_amount"),
            ("buy_sm_amount_rate", "buy_sm_amount_rate"),
        )
