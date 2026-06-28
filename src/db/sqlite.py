from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, List, Sequence

from src.config import LOCAL_SQLITE_DB_PATH


BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_SQLITE_DB_PATH = LOCAL_SQLITE_DB_PATH
DEFAULT_SQLITE_DDL_FILES = (
    BASE_DIR / "DDL/001_create_moneyflow_cnt_ths_d1.sql",
    BASE_DIR / "DDL/002_create_moneyflow_ind_dc_d1.sql",
    BASE_DIR / "DDL/004_create_moneyflow_d1.sql",
    BASE_DIR / "DDL/005_create_moneyflow_dc_d1.sql",
    BASE_DIR / "DDL/006_create_moneyflow_ths_d1.sql",
    BASE_DIR / "DDL/007_create_daily_d1.sql",
)


@dataclass(frozen=True)
class SQLiteConfig:
    database_path: Path = DEFAULT_SQLITE_DB_PATH
    ddl_files: Sequence[Path] = DEFAULT_SQLITE_DDL_FILES


class SQLiteClient:
    def __init__(self, config: SQLiteConfig | None = None) -> None:
        self.config = config or SQLiteConfig()
        self.database_path = self.config.database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize_schema()

    def execute(self, sql: str, params: Sequence[Any] | None = None) -> sqlite3.Cursor:
        with self.connect() as connection:
            return connection.execute(sql, list(params or []))

    def executemany(
        self,
        sql: str,
        rows: Iterable[Sequence[Any]],
        batch_size: int = 100,
    ) -> List[sqlite3.Cursor]:
        results: List[sqlite3.Cursor] = []
        batch: list[Sequence[Any]] = []

        for row in rows:
            batch.append(row)
            if len(batch) >= batch_size:
                results.append(self.execute_batch(sql, batch))
                batch = []

        if batch:
            results.append(self.execute_batch(sql, batch))

        return results

    def execute_batch(self, sql: str, rows: Sequence[Sequence[Any]]) -> sqlite3.Cursor:
        with self.connect() as connection:
            return connection.executemany(sql, rows)

    def fetch_all(self, sql: str, params: Sequence[Any] | None = None) -> list[dict[str, Any]]:
        with self.connect() as connection:
            cursor = connection.execute(sql, list(params or []))
            return [dict(row) for row in cursor.fetchall()]

    def initialize_schema(self) -> None:
        with self.connect() as connection:
            for ddl_file in self.config.ddl_files:
                connection.executescript(ddl_file.read_text(encoding="utf-8"))

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection
