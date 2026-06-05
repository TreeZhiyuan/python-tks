from __future__ import annotations

import argparse

from src.db.d1 import D1Client
from src.repositories.moneyflow_ths_repository import MoneyflowThsRepository


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read moneyflow_ths rows from Cloudflare D1 by trade date.",
    )
    parser.add_argument("--trade-date", required=True, help="Trade date in YYYYMMDD format.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repository = MoneyflowThsRepository(D1Client())
    rows = repository.find_by_trade_date(args.trade_date)

    print(f"trade_date={args.trade_date}, rows={len(rows)}")
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
