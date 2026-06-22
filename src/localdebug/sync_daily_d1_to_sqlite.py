from __future__ import annotations

import argparse
import traceback
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, List

from src.db.client import build_database_client
from src.db.sqlite import DEFAULT_SQLITE_DB_PATH
from src.repositories.daily_repository import DailyRepository


DEFAULT_BATCH_SIZE = 100


def parse_date(value: str) -> date:
    normalized_value = value.replace("-", "")
    try:
        return datetime.strptime(normalized_value, "%Y%m%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid date '{value}'. Expected YYYYMMDD or YYYY-MM-DD."
        ) from exc


def parse_positive_int(value: str) -> int:
    try:
        parsed_value = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("value must be an integer.") from exc

    if parsed_value <= 0:
        raise argparse.ArgumentTypeError("value must be greater than 0.")
    return parsed_value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync daily rows from Cloudflare D1 into local SQLite.",
    )
    parser.add_argument(
        "start_date",
        type=parse_date,
        help="Date to sync, or range start date. Format: YYYYMMDD or YYYY-MM-DD.",
    )
    parser.add_argument(
        "end_date",
        nargs="?",
        type=parse_date,
        help="Optional range end date. Format: YYYYMMDD or YYYY-MM-DD.",
    )
    parser.add_argument(
        "--sqlite-db-path",
        type=Path,
        default=DEFAULT_SQLITE_DB_PATH,
        help=f"Local SQLite database path. Default: {DEFAULT_SQLITE_DB_PATH}",
    )
    parser.add_argument(
        "--batch-size",
        type=parse_positive_int,
        default=DEFAULT_BATCH_SIZE,
        help=f"Rows written to SQLite per batch. Default: {DEFAULT_BATCH_SIZE}.",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue syncing later dates when one date fails.",
    )
    parser.add_argument(
        "--debug-traceback",
        action="store_true",
        help="Print Python traceback when an error occurs.",
    )

    args = parser.parse_args()
    if args.end_date is None:
        args.end_date = args.start_date

    if args.start_date > args.end_date:
        parser.error("start_date must be earlier than or equal to end_date.")
    return args


def build_date_range(start_date: date, end_date: date) -> List[date]:
    trade_dates: List[date] = []
    current_date = start_date
    while current_date <= end_date:
        trade_dates.append(current_date)
        current_date += timedelta(days=1)
    return trade_dates


def convert_db_rows_to_source_rows(
    rows: list[dict[str, Any]],
    repository: DailyRepository,
) -> list[dict[str, Any]]:
    return [
        {
            source_field: row.get(db_field)
            for source_field, db_field in repository.source_to_db_field_map
        }
        for row in rows
    ]


def count_local_daily_rows(sqlite_client: Any, trade_date: str) -> int:
    rows = sqlite_client.fetch_all(
        "SELECT COUNT(*) AS row_count FROM daily WHERE trade_date = ?",
        [trade_date],
    )
    if not rows:
        return 0
    return int(rows[0].get("row_count") or 0)


def sync_one_date(
    trade_date: date,
    d1_repository: DailyRepository,
    sqlite_repository: DailyRepository,
    sqlite_client: Any,
    batch_size: int,
) -> tuple[int, int, int]:
    trade_date_str = trade_date.strftime("%Y%m%d")
    print(f"[INFO] {trade_date_str}: querying Cloudflare D1 daily rows.")

    d1_rows = d1_repository.find_by_trade_date(trade_date_str)
    print(f"[INFO] {trade_date_str}: fetched {len(d1_rows)} row(s) from D1.")

    if not d1_rows:
        local_count = count_local_daily_rows(sqlite_client, trade_date_str)
        print(f"[INFO] {trade_date_str}: no D1 rows to write. local_count={local_count}.")
        return 0, 0, local_count

    source_rows = convert_db_rows_to_source_rows(d1_rows, sqlite_repository)
    written_count = sqlite_repository.upsert_rows_in_batches(
        source_rows,
        batch_size=batch_size,
    )
    local_count = count_local_daily_rows(sqlite_client, trade_date_str)
    print(
        f"[INFO] {trade_date_str}: wrote {written_count} row(s) to SQLite; "
        f"local_count={local_count}."
    )
    return len(d1_rows), written_count, local_count


def main() -> None:
    args = parse_args()
    trade_dates = build_date_range(args.start_date, args.end_date)

    print("[INFO] Preparing database clients.")
    print(f"[INFO] Local SQLite path: {args.sqlite_db_path}")
    try:
        d1_client = build_database_client(use_local_sqlite=False)
        sqlite_client = build_database_client(
            use_local_sqlite=True,
            sqlite_db_path=args.sqlite_db_path,
        )
    except Exception as exc:
        print(f"[ERROR] Failed to initialize database clients: {exc}")
        if args.debug_traceback:
            traceback.print_exc()
        raise SystemExit(1) from exc

    d1_repository = DailyRepository(d1_client)
    sqlite_repository = DailyRepository(sqlite_client)
    total_fetched = 0
    total_written = 0
    empty_dates = 0
    failed_dates = 0

    print(f"[INFO] Syncing {len(trade_dates)} date(s).")
    for index, trade_date in enumerate(trade_dates, start=1):
        trade_date_str = trade_date.strftime("%Y%m%d")
        print(f"[INFO] [{index}/{len(trade_dates)}] Start date={trade_date_str}.")
        try:
            fetched_count, written_count, _ = sync_one_date(
                trade_date,
                d1_repository,
                sqlite_repository,
                sqlite_client,
                batch_size=args.batch_size,
            )
        except Exception as exc:
            failed_dates += 1
            print(f"[ERROR] {trade_date_str}: sync failed: {exc}")
            if args.debug_traceback:
                traceback.print_exc()
            if not args.continue_on_error:
                print("[ERROR] Stop on first failure. Use --continue-on-error to keep going.")
                raise SystemExit(1) from exc
            continue

        total_fetched += fetched_count
        total_written += written_count
        if fetched_count == 0:
            empty_dates += 1

    print(
        "[INFO] Sync finished. "
        f"dates={len(trade_dates)}, empty_dates={empty_dates}, "
        f"failed_dates={failed_dates}, fetched={total_fetched}, written={total_written}."
    )

    if failed_dates:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
