from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, List

from src.db.d1 import D1Client


UPSERT_SQL = """
INSERT OR REPLACE INTO moneyflow_cnt_ths (
    trade_date,
    ts_code,
    name,
    lead_stock,
    close_price,
    pct_change,
    industry_index,
    company_num,
    pct_change_stock,
    net_buy_amount,
    net_sell_amount,
    net_amount
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


SELECT_BY_TRADE_DATE_SQL = """
SELECT
    trade_date,
    ts_code,
    name,
    lead_stock,
    close_price,
    pct_change,
    industry_index,
    company_num,
    pct_change_stock,
    net_buy_amount,
    net_sell_amount,
    net_amount
FROM moneyflow_cnt_ths
WHERE trade_date = ?
ORDER BY ts_code
"""


@dataclass
class MoneyflowCntThsRepository:
    d1_client: D1Client

    def upsert_rows(self, rows: Iterable[dict[str, Any]]) -> int:
        payload: List[list[Any]] = []

        for row in rows:
            payload.append(
                [
                    row.get("trade_date"),
                    row.get("ts_code"),
                    row.get("name"),
                    row.get("lead_stock"),
                    row.get("close"),
                    row.get("pct_change"),
                    row.get("index"),
                    row.get("company_num"),
                    row.get("pct_change_stock"),
                    row.get("net_buy_amount"),
                    row.get("net_sell_amount"),
                    row.get("net_amount"),
                ]
            )

        if not payload:
            return 0

        self.d1_client.executemany(UPSERT_SQL, payload)
        return len(payload)

    def find_by_trade_date(self, trade_date: str) -> list[dict[str, Any]]:
        return self.d1_client.fetch_all(SELECT_BY_TRADE_DATE_SQL, [trade_date])
