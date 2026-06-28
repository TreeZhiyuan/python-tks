from __future__ import annotations

import argparse

from src.localdebug.common import (
    add_sqlite_db_path_arg,
    build_local_sqlite_client,
    parse_date,
)
from src.tasks.dc_index import DEFAULT_IDX_TYPE, DcIndexTask


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch Tushare dc_index rows and write them into local SQLite.",
    )
    parser.add_argument(
        "--ts-code",
        help="Index code. Supports multiple codes separated by commas.",
    )
    parser.add_argument(
        "--name",
        help="Board name, for example 人形机器人.",
    )
    parser.add_argument(
        "--trade-date",
        type=parse_date,
        help="Trade date. Defaults to today's date in Asia/Shanghai. Format: YYYYMMDD or YYYY-MM-DD.",
    )
    parser.add_argument(
        "--start-date",
        type=parse_date,
        help="Start date. Format: YYYYMMDD or YYYY-MM-DD.",
    )
    parser.add_argument(
        "--end-date",
        type=parse_date,
        help="End date. Format: YYYYMMDD or YYYY-MM-DD.",
    )
    parser.add_argument(
        "--idx-type",
        default=DEFAULT_IDX_TYPE,
        help=f"Board type. Default: {DEFAULT_IDX_TYPE}",
    )
    add_sqlite_db_path_arg(parser)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sqlite_client = build_local_sqlite_client(args.sqlite_db_path)
    task = DcIndexTask(db_client=sqlite_client)
    result = task.run(
        trade_date=args.trade_date,
        ts_code=args.ts_code,
        name=args.name,
        start_date=format_date(args.start_date),
        end_date=format_date(args.end_date),
        idx_type=args.idx_type,
    )
    print(f"sqlite_db_path={args.sqlite_db_path}")
    print(
        f"task={result.task_name}, trade_date={result.trade_date}, "
        f"rows={result.row_count}, written={result.written_count}"
    )


def format_date(value) -> str | None:
    return value.strftime("%Y%m%d") if value else None


if __name__ == "__main__":
    main()

