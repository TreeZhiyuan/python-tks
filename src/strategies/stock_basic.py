from __future__ import annotations

from src.strategies.base import BaseStrategy, StrategyContext, StrategyMatch


class StockPoolStrategy(BaseStrategy):
    name = "stock_pool"
    description = "当前 stock_basic 快照股票池中的全部股票"

    def run(self, context: StrategyContext) -> list[StrategyMatch]:
        return [
            StrategyMatch(
                ts_code=str(row["ts_code"]),
                reason="股票存在于当前 stock_basic 快照股票池",
            )
            for row in context.stock_basic_rows()
            if row.get("ts_code")
        ]


class HasIndustryStrategy(BaseStrategy):
    name = "has_industry"
    description = "股票基础信息中已包含行业分类"

    def run(self, context: StrategyContext) -> list[StrategyMatch]:
        matches: list[StrategyMatch] = []
        for row in context.stock_basic_rows():
            ts_code = row.get("ts_code")
            industry = row.get("industry")
            if ts_code and industry:
                matches.append(
                    StrategyMatch(
                        ts_code=str(ts_code),
                        reason=f"industry={industry}",
                        data={"industry": industry},
                    )
                )
        return matches


class HsConnectStrategy(BaseStrategy):
    name = "hs_connect"
    description = "沪深股通标的股票"

    def run(self, context: StrategyContext) -> list[StrategyMatch]:
        matches: list[StrategyMatch] = []
        for row in context.stock_basic_rows():
            ts_code = row.get("ts_code")
            is_hs = row.get("is_hs")
            if ts_code and is_hs in {"H", "S"}:
                matches.append(
                    StrategyMatch(
                        ts_code=str(ts_code),
                        reason=f"is_hs={is_hs}",
                        data={"is_hs": is_hs},
                    )
                )
        return matches
