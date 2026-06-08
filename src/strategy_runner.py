from __future__ import annotations

import argparse
from datetime import date, datetime
from pathlib import Path
from typing import Any

from src.screening.result_store import StrategyResultStore
from src.strategies.base import BaseStrategy, StrategyContext, StrategyMatch
from src.strategies.registry import (
    available_strategies,
    available_strategy_names,
    get_strategy,
    resolve_strategy_names,
)
from src.utils import china_today


def parse_run_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y%m%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Invalid date '{value}'. Expected format: YYYYMMDD.") from exc


def parse_args() -> argparse.Namespace:
    strategy_choices = ["all", *available_strategy_names()]
    parser = argparse.ArgumentParser(
        description="Run stock screening strategies and write JSON result files.",
    )
    parser.add_argument(
        "--strategies",
        nargs="+",
        choices=strategy_choices,
        default=["stock_pool"],
        help="One or more strategies to run. Use 'all' to run every registered strategy.",
    )
    parser.add_argument(
        "--mode",
        choices=["intersection", "union"],
        default="intersection",
        help="How to combine multiple strategy results.",
    )
    parser.add_argument(
        "--run-date",
        type=parse_run_date,
        help="Strategy run date in YYYYMMDD format. Defaults to today in Asia/Shanghai.",
    )
    parser.add_argument(
        "--output-dir",
        default="data/strategy_results",
        help="Directory for JSON strategy result files.",
    )
    parser.add_argument(
        "--list-strategies",
        action="store_true",
        help="List available strategies and exit.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.list_strategies:
        for strategy in available_strategies():
            print(f"{strategy.name}: {strategy.description}")
        return

    strategy_names = resolve_strategy_names(args.strategies)
    strategies = [get_strategy(strategy_name) for strategy_name in strategy_names]
    context = StrategyContext()
    run_date = (args.run_date or china_today()).strftime("%Y%m%d")

    rows = combine_strategy_results(strategies, context, args.mode)
    output_file = StrategyResultStore(Path(args.output_dir)).write_result(
        run_date=run_date,
        mode=args.mode,
        strategy_names=strategy_names,
        strategy_descriptions={strategy.name: strategy.description for strategy in strategies},
        rows=rows,
    )

    print(
        f"strategies={','.join(strategy_names)}, "
        f"mode={args.mode}, "
        f"rows={len(rows)}, "
        f"output={output_file}"
    )


def combine_strategy_results(
    strategies: list[BaseStrategy],
    context: StrategyContext,
    mode: str,
) -> list[dict[str, Any]]:
    matches_by_strategy = {
        strategy.name: {match.ts_code: match for match in strategy.run(context)}
        for strategy in strategies
    }
    match_sets = [set(matches.keys()) for matches in matches_by_strategy.values()]

    if not match_sets:
        selected_codes: set[str] = set()
    elif mode == "intersection":
        selected_codes = set.intersection(*match_sets)
    else:
        selected_codes = set.union(*match_sets)

    stock_basic_by_code = context.stock_basic_by_code()
    return [
        build_result_row(ts_code, stock_basic_by_code.get(ts_code, {}), matches_by_strategy)
        for ts_code in sorted(selected_codes)
    ]


def build_result_row(
    ts_code: str,
    stock_basic: dict[str, Any],
    matches_by_strategy: dict[str, dict[str, StrategyMatch]],
) -> dict[str, Any]:
    matched_strategies = [
        strategy_name
        for strategy_name, matches in matches_by_strategy.items()
        if ts_code in matches
    ]
    strategy_reasons = {
        strategy_name: matches[ts_code].reason
        for strategy_name, matches in matches_by_strategy.items()
        if ts_code in matches
    }
    strategy_data = {
        strategy_name: matches[ts_code].data
        for strategy_name, matches in matches_by_strategy.items()
        if ts_code in matches and matches[ts_code].data
    }
    scores = [
        matches[ts_code].score
        for matches in matches_by_strategy.values()
        if ts_code in matches and matches[ts_code].score is not None
    ]
    row = {
        "ts_code": ts_code,
        "symbol": stock_basic.get("symbol"),
        "name": stock_basic.get("name"),
        "area": stock_basic.get("area"),
        "industry": stock_basic.get("industry"),
        "market": stock_basic.get("market"),
        "exchange": stock_basic.get("exchange"),
        "list_date": stock_basic.get("list_date"),
        "is_hs": stock_basic.get("is_hs"),
        "matched_strategies": matched_strategies,
        "strategy_reasons": strategy_reasons,
    }
    if strategy_data:
        row["strategy_data"] = strategy_data
    if scores:
        row["score"] = sum(scores)
    return row


if __name__ == "__main__":
    main()
