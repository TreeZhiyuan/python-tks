from __future__ import annotations

import argparse
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

from src.localdebug.common import add_sqlite_db_path_arg, parse_date


DEFAULT_INTERVAL_SECONDS = 180
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
    parser = argparse.ArgumentParser(
        description="Run moneyflow Tushare tasks one by one and write rows into local SQLite.",
    )
    parser.add_argument(
        "trade_date",
        type=parse_date,
        help="Trade date to fetch. Format: YYYYMMDD or YYYY-MM-DD.",
    )
    parser.add_argument(
        "--tasks",
        nargs="+",
        choices=DEFAULT_MONEYFLOW_TASKS,
        default=list(DEFAULT_MONEYFLOW_TASKS),
        help="Moneyflow tasks to run. Defaults to all moneyflow tasks.",
    )
    parser.add_argument(
        "--interval-seconds",
        type=parse_non_negative_int,
        default=DEFAULT_INTERVAL_SECONDS,
        help=f"Seconds to wait between tasks. Default: {DEFAULT_INTERVAL_SECONDS}.",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue running later tasks when one task fails.",
    )
    add_sqlite_db_path_arg(parser)
    return parser.parse_args()


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
    trade_date_str = args.trade_date.strftime("%Y%m%d")
    failed_tasks: list[str] = []

    print(f"[INFO] trade_date={trade_date_str}")
    print(f"[INFO] sqlite_db_path={args.sqlite_db_path}")
    print(f"[INFO] tasks={', '.join(args.tasks)}")

    for index, task_name in enumerate(args.tasks, start=1):
        command = build_command(task_name, args.trade_date, args.sqlite_db_path)
        print(f"[INFO] [{index}/{len(args.tasks)}] Running: {subprocess.list2cmdline(command)}")
        result = subprocess.run(command, cwd=project_root)

        if result.returncode != 0:
            failed_tasks.append(task_name)
            print(f"[ERROR] task={task_name} failed with exit_code={result.returncode}.")
            if not args.continue_on_error:
                print("[ERROR] Stop on first failure. Use --continue-on-error to keep going.")
                raise SystemExit(result.returncode)
        else:
            print(f"[INFO] task={task_name} completed successfully.")

        if index < len(args.tasks) and args.interval_seconds > 0:
            print(f"[INFO] Waiting {args.interval_seconds} second(s) before the next task.")
            time.sleep(args.interval_seconds)

    if failed_tasks:
        print(f"[ERROR] Failed task(s): {', '.join(failed_tasks)}")
        raise SystemExit(1)

    print(f"[INFO] All moneyflow tasks completed for trade_date={trade_date_str}.")


if __name__ == "__main__":
    main()
