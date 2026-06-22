from __future__ import annotations

import argparse
import subprocess
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List


DEFAULT_INTERVAL_SECONDS = 180


def parse_date(value: str) -> date:
    normalized_value = value.replace("-", "")
    try:
        return datetime.strptime(normalized_value, "%Y%m%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid date '{value}'. Expected YYYYMMDD or YYYY-MM-DD."
        ) from exc


def parse_non_negative_int(value: str) -> int:
    try:
        parsed_value = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("value must be an integer.") from exc

    if parsed_value < 0:
        raise argparse.ArgumentTypeError("value must be greater than or equal to 0.")
    return parsed_value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the daily local SQLite task for every day in a date range.",
    )
    parser.add_argument(
        "start_date",
        type=parse_date,
        help="Start date, for example 20240501 or 2024-05-01.",
    )
    parser.add_argument(
        "end_date",
        type=parse_date,
        help="End date, for example 20240531 or 2024-05-31.",
    )
    parser.add_argument(
        "--interval-seconds",
        type=parse_non_negative_int,
        default=DEFAULT_INTERVAL_SECONDS,
        help="Seconds to wait between dates. Default: 180.",
    )
    args = parser.parse_args()
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


def is_weekend(current_date: date) -> bool:
    return current_date.weekday() >= 5


def build_command(trade_date: date) -> list[str]:
    return [
        sys.executable,
        "-m",
        "src.main",
        "--tasks",
        "daily",
        "--dates",
        trade_date.strftime("%Y%m%d"),
        "--local-sqlite",
    ]


def main() -> None:
    args = parse_args()
    trade_dates = build_date_range(args.start_date, args.end_date)
    project_root = Path(__file__).resolve().parents[2]

    for index, trade_date in enumerate(trade_dates, start=1):
        if is_weekend(trade_date):
            print(f"[{index}/{len(trade_dates)}] Skipping weekend date: {trade_date:%Y%m%d}")
            continue

        command = build_command(trade_date)
        print(f"[{index}/{len(trade_dates)}] Running: {subprocess.list2cmdline(command)}")
        result = subprocess.run(command, cwd=project_root)
        if result.returncode != 0:
            raise SystemExit(result.returncode)

        if index < len(trade_dates) and args.interval_seconds > 0:
            print(f"Waiting {args.interval_seconds} second(s) before the next date.")
            time.sleep(args.interval_seconds)


if __name__ == "__main__":
    main()
