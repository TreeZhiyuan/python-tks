from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from src.db.client import DatabaseClient
from src.repositories.base import BaseD1Repository


@dataclass
class MoneyflowCntThsRepository(BaseD1Repository):
    db_client: DatabaseClient

    @property
    def table_name(self) -> str:
        return "moneyflow_cnt_ths"

    @property
    def select_columns(self) -> Sequence[str]:
        return (
            "trade_date",
            "ts_code",
            "name",
            "lead_stock",
            "close_price",
            "pct_change",
            "industry_index",
            "company_num",
            "pct_change_stock",
            "net_buy_amount",
            "net_sell_amount",
            "net_amount",
        )

    @property
    def source_to_db_field_map(self) -> Sequence[tuple[str, str]]:
        return (
            ("trade_date", "trade_date"),
            ("ts_code", "ts_code"),
            ("name", "name"),
            ("lead_stock", "lead_stock"),
            ("close", "close_price"),
            ("pct_change", "pct_change"),
            ("index", "industry_index"),
            ("company_num", "company_num"),
            ("pct_change_stock", "pct_change_stock"),
            ("net_buy_amount", "net_buy_amount"),
            ("net_sell_amount", "net_sell_amount"),
            ("net_amount", "net_amount"),
        )
