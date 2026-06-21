from __future__ import annotations

import argparse
from pathlib import Path

from src.db.client import build_database_client
from src.db.sqlite import DEFAULT_SQLITE_DB_PATH


def add_database_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--local-sqlite",
        action="store_true",
        help=f"Read from local SQLite instead of Cloudflare D1. Default path: {DEFAULT_SQLITE_DB_PATH}",
    )
    parser.add_argument(
        "--sqlite-db-path",
        type=Path,
        default=DEFAULT_SQLITE_DB_PATH,
        help="Local SQLite database path used with --local-sqlite.",
    )


def build_read_database_client(args: argparse.Namespace):
    return build_database_client(
        use_local_sqlite=args.local_sqlite,
        sqlite_db_path=args.sqlite_db_path,
    )
