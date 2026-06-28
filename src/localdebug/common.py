from __future__ import annotations

import argparse
from datetime import date, datetime
from pathlib import Path
from typing import Any

from src.db.client import build_database_client
from src.db.sqlite import DEFAULT_SQLITE_DB_PATH


def parse_date(value: str) -> date:
    normalized_value = value.replace("-", "")
    try:
        return datetime.strptime(normalized_value, "%Y%m%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid date '{value}'. Expected YYYYMMDD or YYYY-MM-DD."
        ) from exc


def add_sqlite_db_path_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--sqlite-db-path",
        type=Path,
        default=DEFAULT_SQLITE_DB_PATH,
        help=f"Local SQLite database path. Default: {DEFAULT_SQLITE_DB_PATH}",
    )


def build_local_sqlite_client(sqlite_db_path: Path) -> Any:
    return build_database_client(
        use_local_sqlite=True,
        sqlite_db_path=sqlite_db_path,
    )

