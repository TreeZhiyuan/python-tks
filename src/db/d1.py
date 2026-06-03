from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, List, Sequence

from cloudflare import Cloudflare

from src.config import (
    CLOUDFLARE_ACCOUNT_ID,
    CLOUDFLARE_API_TOKEN,
    CLOUDFLARE_D1_DATABASE_ID,
)


def _is_placeholder(value: str, prefix: str = "REPLACE_WITH_") -> bool:
    return not value or value.startswith(prefix)


@dataclass
class D1Config:
    api_token: str = CLOUDFLARE_API_TOKEN
    account_id: str = CLOUDFLARE_ACCOUNT_ID
    database_id: str = CLOUDFLARE_D1_DATABASE_ID

    def validate(self) -> None:
        if _is_placeholder(self.api_token):
            raise ValueError("CLOUDFLARE_API_TOKEN is not configured. Please update your .env file.")
        if _is_placeholder(self.account_id):
            raise ValueError("CLOUDFLARE_ACCOUNT_ID is not configured. Please update your .env file.")
        if _is_placeholder(self.database_id):
            raise ValueError("CLOUDFLARE_D1_DATABASE_ID is not configured. Please update your .env file.")


class D1Client:
    def __init__(self, config: D1Config | None = None) -> None:
        self.config = config or D1Config()
        self.config.validate()
        self.client = Cloudflare(api_token=self.config.api_token)

    def execute(self, sql: str, params: Sequence[Any] | None = None) -> Any:
        return self.client.d1.database.query(
            database_id=self.config.database_id,
            account_id=self.config.account_id,
            sql=sql,
            params=list(params or []),
        )

    def executemany(self, sql: str, rows: Iterable[Sequence[Any]]) -> List[Any]:
        results: List[Any] = []
        for row in rows:
            results.append(self.execute(sql, row))
        return results

    def fetch_all(self, sql: str, params: Sequence[Any] | None = None) -> list[dict[str, Any]]:
        response = self.execute(sql, params)

        if isinstance(response, dict):
            result = response.get("result")
            if isinstance(result, list):
                return [item for item in result if isinstance(item, dict)]

        result_attr = getattr(response, "result", None)
        if isinstance(result_attr, list):
            return [item for item in result_attr if isinstance(item, dict)]

        return []
