from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from src.db.d1 import D1Client
from src.repositories.base import BaseD1Repository


@dataclass
class MoneyflowDcRepository(BaseD1Repository):
    d1_client: D1Client

    @property
    def table_name(self) -> str:
        return "moneyflow_dc"

    @property
    def select_columns(self) -> Sequence[str]:
        return (
            "trade_date",
            "ts_code",
            "name",
            "pct_change",
            "close_price",
            "net_amount",
            "net_amount_rate",
            "buy_elg_amount",
            "buy_elg_amount_rate",
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
            ("close", "close_price"),
            ("net_amount", "net_amount"),
            ("net_amount_rate", "net_amount_rate"),
            ("buy_elg_amount", "buy_elg_amount"),
            ("buy_elg_amount_rate", "buy_elg_amount_rate"),
            ("buy_lg_amount", "buy_lg_amount"),
            ("buy_lg_amount_rate", "buy_lg_amount_rate"),
            ("buy_md_amount", "buy_md_amount"),
            ("buy_md_amount_rate", "buy_md_amount_rate"),
            ("buy_sm_amount", "buy_sm_amount"),
            ("buy_sm_amount_rate", "buy_sm_amount_rate"),
        )
