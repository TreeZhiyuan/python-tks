from __future__ import annotations

from src.strategies.base import BaseStrategy
from src.strategies.daily_patterns import (
    BottomBoxConsolidationStrategy,
    BoxConsolidationStrategy,
    HalfYearBottomConsolidationStrategy,
    VolumeDryUpConsolidationStrategy,
)
from src.strategies.stock_basic import HasIndustryStrategy, HsConnectStrategy, StockPoolStrategy


STRATEGY_REGISTRY: dict[str, BaseStrategy] = {
    strategy.name: strategy
    for strategy in (
        StockPoolStrategy(),
        HasIndustryStrategy(),
        HsConnectStrategy(),
        BoxConsolidationStrategy(),
        VolumeDryUpConsolidationStrategy(),
        HalfYearBottomConsolidationStrategy(),
        BottomBoxConsolidationStrategy(),
    )
}


def available_strategy_names() -> list[str]:
    return list(STRATEGY_REGISTRY.keys())


def available_strategies() -> list[BaseStrategy]:
    return list(STRATEGY_REGISTRY.values())


def get_strategy(strategy_name: str) -> BaseStrategy:
    try:
        return STRATEGY_REGISTRY[strategy_name]
    except KeyError as exc:
        available = ", ".join(available_strategy_names())
        raise ValueError(f"Unknown strategy '{strategy_name}'. Available strategies: {available}") from exc


def resolve_strategy_names(strategy_names: list[str]) -> list[str]:
    if "all" in strategy_names:
        return available_strategy_names()

    seen: set[str] = set()
    resolved: list[str] = []
    for strategy_name in strategy_names:
        if strategy_name not in STRATEGY_REGISTRY:
            available = ", ".join(["all", *available_strategy_names()])
            raise ValueError(f"Unknown strategy '{strategy_name}'. Available strategies: {available}")
        if strategy_name not in seen:
            seen.add(strategy_name)
            resolved.append(strategy_name)
    return resolved
