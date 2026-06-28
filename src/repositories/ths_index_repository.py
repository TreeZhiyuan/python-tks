from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from src.db.client import DatabaseClient
from src.repositories.base import BaseD1Repository


@dataclass
class ThsIndexRepository(BaseD1Repository):
    db_client: DatabaseClient

    @property
    def table_name(self) -> str:
        return "ths_index"

    @property
    def select_columns(self) -> Sequence[str]:
        return (
            "ts_code",
            "name",
            "count",
            "exchange",
            "list_date",
            "type",
        )

    @property
    def source_to_db_field_map(self) -> Sequence[tuple[str, str]]:
        return (
            ("ts_code", "ts_code"),
            ("name", "name"),
            ("count", "count"),
            ("exchange", "exchange"),
            ("list_date", "list_date"),
            ("type", "type"),
        )

