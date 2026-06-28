from __future__ import annotations

import argparse

from src.localdebug.common import add_sqlite_db_path_arg, build_local_sqlite_client
from src.tasks.ths_index import ThsIndexTask


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch Tushare ths_index rows and write them into local SQLite.",
    )
    parser.add_argument(
        "--ts-code",
        help="Index code, for example 885835.TI. Supports the original Tushare ts_code input.",
    )
    parser.add_argument(
        "--exchange",
        help="Market type: A-a股, HK-港股, US-美股.",
    )
    parser.add_argument(
        "--type",
        dest="type_",
        help="Index type: N-概念指数, I-行业指数, R-地域指数, S-特色指数, ST-风格指数, TH-主题指数, BB-宽基指数.",
    )
    add_sqlite_db_path_arg(parser)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sqlite_client = build_local_sqlite_client(args.sqlite_db_path)
    task = ThsIndexTask(db_client=sqlite_client)
    result = task.run(
        ts_code=args.ts_code,
        exchange=args.exchange,
        type_=args.type_,
    )
    print(f"sqlite_db_path={args.sqlite_db_path}")
    print(
        f"task={result.task_name}, scope=snapshot, "
        f"rows={result.row_count}, written={result.written_count}"
    )


if __name__ == "__main__":
    main()

