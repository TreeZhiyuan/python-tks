from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.db.client import DatabaseClient, build_database_client
from src.db.sqlite import DEFAULT_SQLITE_DB_PATH
from src.repositories.daily_repository import DailyRepository
from src.storage.json_store import JsonSnapshotStore


@dataclass(frozen=True)
class StrategyMatch:
    ts_code: str
    reason: str
    score: float | None = None
    data: dict[str, Any] = field(default_factory=dict)


class StrategyContext:
    def __init__(
        self,
        stock_basic_store: JsonSnapshotStore | None = None,
        daily_repository: DailyRepository | None = None,
        sqlite_db_path: Path | None = None,
        run_date: str | None = None,
    ) -> None:
        self.stock_basic_store = stock_basic_store or JsonSnapshotStore(Path("data/stock_basic"))
        self.sqlite_db_path = sqlite_db_path or DEFAULT_SQLITE_DB_PATH
        self.run_date = run_date
        self._daily_repository = daily_repository
        self._daily_db_client: DatabaseClient | None = None
        self._stock_basic_rows: list[dict[str, Any]] | None = None
        self._stock_basic_by_code: dict[str, dict[str, Any]] | None = None
        self._daily_rows_cache: dict[int, dict[str, list[dict[str, Any]]]] = {}

    def stock_basic_rows(self) -> list[dict[str, Any]]:
        if self._stock_basic_rows is None:
            snapshot = self.stock_basic_store.read_snapshot("stock_basic")
            rows = snapshot.get("rows", [])
            self._stock_basic_rows = [row for row in rows if isinstance(row, dict)]
        return self._stock_basic_rows

    def stock_basic_by_code(self) -> dict[str, dict[str, Any]]:
        if self._stock_basic_by_code is None:
            self._stock_basic_by_code = {
                str(row["ts_code"]): row
                for row in self.stock_basic_rows()
                if row.get("ts_code")
            }
        return self._stock_basic_by_code

    def stock_codes(self) -> list[str]:
        return sorted(self.stock_basic_by_code())

    def daily_repository(self) -> DailyRepository:
        if self._daily_repository is None:
            self._daily_db_client = build_database_client(
                use_local_sqlite=True,
                sqlite_db_path=self.sqlite_db_path,
            )
            self._daily_repository = DailyRepository(self._daily_db_client)
        return self._daily_repository

    def recent_daily_rows_by_code(self, lookback_days: int) -> dict[str, list[dict[str, Any]]]:
        if lookback_days in self._daily_rows_cache:
            return self._daily_rows_cache[lookback_days]

        rows = self.daily_repository().find_recent_by_ts_codes(
            self.stock_codes(),
            limit_per_code=lookback_days,
            end_trade_date=self.run_date,
        )
        rows_by_code: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            ts_code = row.get("ts_code")
            if ts_code:
                rows_by_code.setdefault(str(ts_code), []).append(row)
        self._daily_rows_cache[lookback_days] = rows_by_code
        return rows_by_code


class BaseStrategy(ABC):
    name: str
    description: str

    @abstractmethod
    def run(self, context: StrategyContext) -> list[StrategyMatch]:
        raise NotImplementedError
