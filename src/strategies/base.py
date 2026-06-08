from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.storage.json_store import JsonSnapshotStore


@dataclass(frozen=True)
class StrategyMatch:
    ts_code: str
    reason: str
    score: float | None = None
    data: dict[str, Any] = field(default_factory=dict)


class StrategyContext:
    def __init__(self, stock_basic_store: JsonSnapshotStore | None = None) -> None:
        self.stock_basic_store = stock_basic_store or JsonSnapshotStore(Path("data/stock_basic"))
        self._stock_basic_rows: list[dict[str, Any]] | None = None
        self._stock_basic_by_code: dict[str, dict[str, Any]] | None = None

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


class BaseStrategy(ABC):
    name: str
    description: str

    @abstractmethod
    def run(self, context: StrategyContext) -> list[StrategyMatch]:
        raise NotImplementedError
