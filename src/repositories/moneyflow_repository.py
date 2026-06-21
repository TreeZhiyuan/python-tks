from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from src.db.client import DatabaseClient
from src.repositories.base import BaseD1Repository


@dataclass
class MoneyflowRepository(BaseD1Repository):
    db_client: DatabaseClient

    @property
    def table_name(self) -> str:
        return "moneyflow"

    @property
    def select_columns(self) -> Sequence[str]:
        return (
            "ts_code",
            "trade_date",
            "buy_sm_vol",
            "buy_sm_amount",
            "sell_sm_vol",
            "sell_sm_amount",
            "buy_md_vol",
            "buy_md_amount",
            "sell_md_vol",
            "sell_md_amount",
            "buy_lg_vol",
            "buy_lg_amount",
            "sell_lg_vol",
            "sell_lg_amount",
            "buy_elg_vol",
            "buy_elg_amount",
            "sell_elg_vol",
            "sell_elg_amount",
            "net_mf_vol",
            "net_mf_amount",
        )

    @property
    def source_to_db_field_map(self) -> Sequence[tuple[str, str]]:
        return tuple((field, field) for field in self.select_columns)
