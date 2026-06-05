from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta
from typing import Iterable, List

from src.core.models import TaskRunResult
from src.tasks.registry import (
    available_task_names,
    build_task,
    get_task_definition,
    resolve_task_names,
)
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
    task_choices = ["all", *available_task_names()]
    parser = argparse.ArgumentParser(
        description="Fetch Tushare board moneyflow data and write rows into Cloudflare D1.",
    )
    parser.add_argument(
        "--tasks",
        nargs="+",
        choices=task_choices,
        default=["moneyflow_cnt_ths"],
        help="One or more tasks to run. Use 'all' to run every registered task.",
    )
    parser.add_argument(
        "--task",
        choices=task_choices,
        help="Deprecated alias for --tasks. Accepts one task name or 'all'.",
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

    if args.task:
        args.tasks = [args.task]

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
    task_names = resolve_task_names(args.tasks)
    completed_count = 0

    for task_name in task_names:
        task_definition = get_task_definition(task_name)
        task = build_task(task_name)
        results = task.run_many(trade_dates) if task_definition.uses_trade_date else [task.run()]
        completed_count += len(results)

        for result in results:
            print(format_result(result))

    print(f"Completed {completed_count} task/date run(s).")


def format_result(result: TaskRunResult) -> str:
    target = f"trade_date={result.trade_date}" if result.trade_date else "scope=snapshot"
    output = f", output={result.output_path}" if result.output_path else ""
    return (
        f"task={result.task_name}, "
        f"{target}, "
        f"rows={result.row_count}, "
        f"written={result.written_count}"
        f"{output}"
    )


if __name__ == "__main__":
    main()
