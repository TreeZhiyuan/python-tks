from __future__ import annotations

import argparse
import subprocess
import sys
import time
from datetime import date, timedelta
from pathlib import Path

from src.localdebug.common import add_sqlite_db_path_arg, parse_date


DEFAULT_INTERVAL_SECONDS = 80
DEFAULT_MONEYFLOW_TASKS = (
    "moneyflow_cnt_ths",
    "moneyflow_ind_dc",
    "moneyflow",
    "moneyflow_dc",
    "moneyflow_ths",
)


def parse_non_negative_int(value: str) -> int:
    try:
        parsed_value = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("value must be an integer.") from exc

    if parsed_value < 0:
        raise argparse.ArgumentTypeError("value must be greater than or equal to 0.")
    return parsed_value


def parse_args() -> argparse.Namespace:
    task_choices = ("all", *DEFAULT_MONEYFLOW_TASKS)
    parser = argparse.ArgumentParser(
        description="Run moneyflow Tushare tasks for every weekday in a date range and write rows into local SQLite.",
    )
    parser.add_argument(
        "start_date",
        type=parse_date,
        help="Start date to fetch. Format: YYYYMMDD or YYYY-MM-DD.",
    )
    parser.add_argument(
        "end_date",
        type=parse_date,
        help="End date to fetch. Format: YYYYMMDD or YYYY-MM-DD.",
    )
    parser.add_argument(
        "--tasks",
        nargs="+",
        choices=task_choices,
        help="Moneyflow tasks to run. Use 'all' to run every moneyflow task. Defaults to all.",
    )
    parser.add_argument(
        "--task",
        nargs="+",
        choices=task_choices,
        help="Alias for --tasks. Accepts one or more moneyflow task names or 'all'.",
    )
    parser.add_argument(
        "--interval-seconds",
        type=parse_non_negative_int,
        default=DEFAULT_INTERVAL_SECONDS,
        help=(
            "Seconds to wait between each date/task run. "
            f"Default: {DEFAULT_INTERVAL_SECONDS}."
        ),
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue running later tasks when one task fails.",
    )
    add_sqlite_db_path_arg(parser)

    args = parser.parse_args()
    if args.start_date > args.end_date:
        parser.error("start_date must be earlier than or equal to end_date.")
    if args.tasks and args.task:
        parser.error("--task cannot be used together with --tasks.")

    requested_tasks = args.tasks or args.task or ["all"]
    args.tasks = resolve_task_names(requested_tasks)
    return args


def resolve_task_names(task_names: list[str]) -> list[str]:
    if "all" in task_names:
        return list(DEFAULT_MONEYFLOW_TASKS)

    seen: set[str] = set()
    resolved: list[str] = []
    for task_name in task_names:
        if task_name not in seen:
            seen.add(task_name)
            resolved.append(task_name)
    return resolved


def build_date_range(start_date: date, end_date: date) -> list[date]:
    trade_dates: list[date] = []
    current_date = start_date
    while current_date <= end_date:
        trade_dates.append(current_date)
        current_date += timedelta(days=1)
    return trade_dates


def is_weekend(current_date: date) -> bool:
    return current_date.weekday() >= 5


def build_command(task_name: str, trade_date: date, sqlite_db_path: Path) -> list[str]:
    return [
        sys.executable,
        "-m",
        "src.main",
        "--tasks",
        task_name,
        "--dates",
        trade_date.strftime("%Y%m%d"),
        "--local-sqlite",
        "--sqlite-db-path",
        str(sqlite_db_path),
    ]


def main() -> None:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[2]
    trade_dates = build_date_range(args.start_date, args.end_date)
    weekday_count = sum(not is_weekend(trade_date) for trade_date in trade_dates)
    total_run_count = weekday_count * len(args.tasks)
    completed_run_count = 0
    failed_runs: list[str] = []

    print(f"[INFO] start_date={args.start_date:%Y%m%d}")
    print(f"[INFO] end_date={args.end_date:%Y%m%d}")
    print(f"[INFO] sqlite_db_path={args.sqlite_db_path}")
    print(f"[INFO] tasks={', '.join(args.tasks)}")
    print(f"[INFO] interval_seconds={args.interval_seconds}")

    for date_index, trade_date in enumerate(trade_dates, start=1):
        trade_date_str = trade_date.strftime("%Y%m%d")
        if is_weekend(trade_date):
            print(f"[INFO] [{date_index}/{len(trade_dates)}] Skipping weekend date: {trade_date_str}")
            continue

        for task_index, task_name in enumerate(args.tasks, start=1):
            completed_run_count += 1
            command = build_command(task_name, trade_date, args.sqlite_db_path)
            print(
                "[INFO] "
                f"[run {completed_run_count}/{total_run_count}] "
                f"[date {date_index}/{len(trade_dates)}] "
                f"[task {task_index}/{len(args.tasks)}] "
                f"Running: {subprocess.list2cmdline(command)}"
            )
            result = subprocess.run(command, cwd=project_root)

            if result.returncode != 0:
                failed_run = f"{trade_date_str}/{task_name}"
                failed_runs.append(failed_run)
                print(
                    f"[ERROR] trade_date={trade_date_str}, task={task_name} "
                    f"failed with exit_code={result.returncode}."
                )
                if not args.continue_on_error:
                    print("[ERROR] Stop on first failure. Use --continue-on-error to keep going.")
                    raise SystemExit(result.returncode)
            else:
                print(f"[INFO] trade_date={trade_date_str}, task={task_name} completed successfully.")

            if completed_run_count < total_run_count and args.interval_seconds > 0:
                print(
                    f"[INFO] Waiting {args.interval_seconds} second(s) "
                    "before the next date/task run."
                )
                time.sleep(args.interval_seconds)

    if failed_runs:
        print(f"[ERROR] Failed run(s): {', '.join(failed_runs)}")
        raise SystemExit(1)

    if total_run_count == 0:
        print("[INFO] No weekday dates to run in the input date range.")
        return

    print(
        "[INFO] All moneyflow task/date runs completed "
        f"for date range {args.start_date:%Y%m%d}-{args.end_date:%Y%m%d}."
    )


if __name__ == "__main__":
    main()
