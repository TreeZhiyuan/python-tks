from __future__ import annotations

from typing import Any

import tushare as ts

from src.config import TUSHARE_TOKEN


class TushareClientFactory:
    def __init__(self, token: str = TUSHARE_TOKEN) -> None:
        self.token = token

    def create_pro_client(self) -> Any:
        if not self.token or self.token == "REPLACE_WITH_YOUR_TUSHARE_TOKEN":
            raise ValueError("TUSHARE_TOKEN is not configured. Please update your .env file.")

        ts.set_token(self.token)
        return ts.pro_api()
