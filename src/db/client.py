from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Protocol, Sequence

from src.db.sqlite import DEFAULT_SQLITE_DB_PATH, SQLiteClient, SQLiteConfig


class DatabaseClient(Protocol):
    def execute(self, sql: str, params: Sequence[Any] | None = None) -> Any:
        ...

    def executemany(
        self,
        sql: str,
        rows: Iterable[Sequence[Any]],
        batch_size: int = 100,
    ) -> list[Any]:
        ...

    def fetch_all(self, sql: str, params: Sequence[Any] | None = None) -> list[dict[str, Any]]:
        ...


def build_database_client(
    use_local_sqlite: bool = False,
    sqlite_db_path: Path | None = None,
) -> DatabaseClient:
    if use_local_sqlite:
        return SQLiteClient(SQLiteConfig(database_path=sqlite_db_path or DEFAULT_SQLITE_DB_PATH))
    from src.db.d1 import D1Client

    return D1Client()
