from __future__ import annotations

import argparse

from src.read_utils import add_database_args, build_read_database_client
from src.repositories.moneyflow_ind_dc_repository import MoneyflowIndDcRepository


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read moneyflow_ind_dc rows from Cloudflare D1 by trade date.",
    )
    parser.add_argument(
        "--trade-date",
        required=True,
        help="Trade date in YYYYMMDD format.",
    )
    add_database_args(parser)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repository = MoneyflowIndDcRepository(build_read_database_client(args))
    rows = repository.find_by_trade_date(args.trade_date)

    print(f"trade_date={args.trade_date}, rows={len(rows)}")
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
