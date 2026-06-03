from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta
from typing import Iterable, List

from src.tasks.moneyflow_cnt_ths import MoneyflowCntThsTask
from src.utils import yesterday


def parse_trade_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y%m%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Invalid date '{value}'. Expected format: YYYYMMDD.") from exc


def build_date_range(start_date: date, end_date: date) -> List[date]:
    if start_date > end_date:
        raise ValueError("start-date must be earlier than or equal to end-date.")

    dates: List[date] = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)
    return dates


def unique_dates(dates: Iterable[date]) -> List[date]:
    seen = set()
    result: List[date] = []
    for current_date in dates:
        if current_date not in seen:
            seen.add(current_date)
            result.append(current_date)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch moneyflow_cnt_ths data and save one CSV per trade date.",
    )
    parser.add_argument(
        "--dates",
        nargs="+",
        type=parse_trade_date,
        help="One or more trade dates in YYYYMMDD format.",
    )
    parser.add_argument(
        "--start-date",
        type=parse_trade_date,
        help="Start date in YYYYMMDD format.",
    )
    parser.add_argument(
        "--end-date",
        type=parse_trade_date,
        help="End date in YYYYMMDD format.",
    )

    args = parser.parse_args()

    if args.dates and (args.start_date or args.end_date):
        parser.error("--dates cannot be used together with --start-date/--end-date.")

    if bool(args.start_date) != bool(args.end_date):
        parser.error("--start-date and --end-date must be used together.")

    return args


def resolve_trade_dates(args: argparse.Namespace) -> List[date]:
    if args.dates:
        return unique_dates(args.dates)

    if args.start_date and args.end_date:
        return build_date_range(args.start_date, args.end_date)

    return [yesterday()]


def main() -> None:
    args = parse_args()
    trade_dates = resolve_trade_dates(args)
    task = MoneyflowCntThsTask()
    results = task.run_many(trade_dates)

    for result in results:
        print(
            f"trade_date={result.trade_date}, "
            f"rows={result.row_count}, "
            f"csv={result.output_file}"
        )

    print(f"Completed {len(results)} date(s).")


if __name__ == "__main__":
    main()
