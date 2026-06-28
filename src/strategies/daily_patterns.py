from __future__ import annotations

from dataclasses import dataclass
from statistics import fmean
from typing import Any, Iterable

from src.strategies.base import BaseStrategy, StrategyContext, StrategyMatch


MIN_CLOSE_PRICE = 1.0


@dataclass(frozen=True)
class DailyMetrics:
    ts_code: str
    days: int
    latest_trade_date: str
    latest_close: float
    high: float
    low: float
    amplitude_pct: float
    close_position_pct: float
    first_avg_close: float
    last_avg_close: float
    trend_pct: float
    latest_vol_avg: float
    previous_vol_avg: float
    volume_shrink_pct: float | None

    def as_data(self) -> dict[str, Any]:
        return {
            "days": self.days,
            "latest_trade_date": self.latest_trade_date,
            "latest_close": round(self.latest_close, 4),
            "high": round(self.high, 4),
            "low": round(self.low, 4),
            "amplitude_pct": round(self.amplitude_pct, 2),
            "close_position_pct": round(self.close_position_pct, 2),
            "first_avg_close": round(self.first_avg_close, 4),
            "last_avg_close": round(self.last_avg_close, 4),
            "trend_pct": round(self.trend_pct, 2),
            "latest_vol_avg": round(self.latest_vol_avg, 2),
            "previous_vol_avg": round(self.previous_vol_avg, 2),
            "volume_shrink_pct": (
                round(self.volume_shrink_pct, 2)
                if self.volume_shrink_pct is not None
                else None
            ),
        }


def compact_box_metrics(rows: list[dict[str, Any]], days: int) -> DailyMetrics | None:
    window = rows[-days:]
    if len(window) < days:
        return None

    close_prices = numeric_values(row.get("close_price") for row in window)
    high_prices = numeric_values(row.get("high_price") for row in window)
    low_prices = numeric_values(row.get("low_price") for row in window)
    volumes = numeric_values(row.get("vol") for row in window)
    if len(close_prices) < days or len(high_prices) < days or len(low_prices) < days:
        return None

    latest_close = close_prices[-1]
    if latest_close < MIN_CLOSE_PRICE:
        return None

    high = max(high_prices)
    low = min(low_prices)
    if low <= 0 or high <= low:
        return None

    first_avg_close = fmean(close_prices[: min(10, len(close_prices))])
    last_avg_close = fmean(close_prices[-min(10, len(close_prices)) :])
    previous_volumes = volumes[: len(volumes) // 2]
    latest_volumes = volumes[len(volumes) // 2 :]
    previous_vol_avg = fmean(previous_volumes) if previous_volumes else 0.0
    latest_vol_avg = fmean(latest_volumes) if latest_volumes else 0.0
    volume_shrink_pct = (
        (latest_vol_avg / previous_vol_avg - 1) * 100
        if previous_vol_avg > 0
        else None
    )

    return DailyMetrics(
        ts_code=str(window[-1]["ts_code"]),
        days=days,
        latest_trade_date=str(window[-1]["trade_date"]),
        latest_close=latest_close,
        high=high,
        low=low,
        amplitude_pct=(high / low - 1) * 100,
        close_position_pct=(latest_close - low) / (high - low) * 100,
        first_avg_close=first_avg_close,
        last_avg_close=last_avg_close,
        trend_pct=(last_avg_close / first_avg_close - 1) * 100
        if first_avg_close > 0
        else 0.0,
        latest_vol_avg=latest_vol_avg,
        previous_vol_avg=previous_vol_avg,
        volume_shrink_pct=volume_shrink_pct,
    )


def numeric_values(values: Iterable[Any]) -> list[float]:
    result: list[float] = []
    for value in values:
        if value is None:
            continue
        try:
            result.append(float(value))
        except (TypeError, ValueError):
            continue
    return result


class BoxConsolidationStrategy(BaseStrategy):
    name = "box_consolidation"
    description = "近60个交易日处于窄幅箱体横盘的股票"
    days = 60
    max_amplitude_pct = 25.0
    max_abs_trend_pct = 8.0
    min_close_position_pct = 20.0
    max_close_position_pct = 85.0

    def run(self, context: StrategyContext) -> list[StrategyMatch]:
        matches: list[StrategyMatch] = []
        for ts_code, rows in context.recent_daily_rows_by_code(self.days).items():
            metrics = compact_box_metrics(rows, self.days)
            if not metrics:
                continue
            if (
                metrics.amplitude_pct <= self.max_amplitude_pct
                and abs(metrics.trend_pct) <= self.max_abs_trend_pct
                and self.min_close_position_pct
                <= metrics.close_position_pct
                <= self.max_close_position_pct
            ):
                matches.append(
                    StrategyMatch(
                        ts_code=ts_code,
                        reason=(
                            f"{self.days}日振幅={metrics.amplitude_pct:.2f}%, "
                            f"均价趋势={metrics.trend_pct:.2f}%"
                        ),
                        score=self.score(metrics),
                        data=metrics.as_data(),
                    )
                )
        return matches

    def score(self, metrics: DailyMetrics) -> float:
        amplitude_score = max(0.0, self.max_amplitude_pct - metrics.amplitude_pct)
        trend_score = max(0.0, self.max_abs_trend_pct - abs(metrics.trend_pct))
        return round(amplitude_score + trend_score, 4)


class VolumeDryUpConsolidationStrategy(BoxConsolidationStrategy):
    name = "volume_dry_up_consolidation"
    description = "近60个交易日横盘且后半段成交量明显萎缩的股票"
    max_amplitude_pct = 30.0
    max_abs_trend_pct = 10.0
    max_volume_shrink_pct = -25.0

    def run(self, context: StrategyContext) -> list[StrategyMatch]:
        matches: list[StrategyMatch] = []
        for ts_code, rows in context.recent_daily_rows_by_code(self.days).items():
            metrics = compact_box_metrics(rows, self.days)
            if not metrics or metrics.volume_shrink_pct is None:
                continue
            if (
                metrics.amplitude_pct <= self.max_amplitude_pct
                and abs(metrics.trend_pct) <= self.max_abs_trend_pct
                and metrics.volume_shrink_pct <= self.max_volume_shrink_pct
            ):
                matches.append(
                    StrategyMatch(
                        ts_code=ts_code,
                        reason=(
                            f"{self.days}日横盘, 后半段均量较前半段"
                            f"{metrics.volume_shrink_pct:.2f}%"
                        ),
                        score=self.score(metrics),
                        data=metrics.as_data(),
                    )
                )
        return matches

    def score(self, metrics: DailyMetrics) -> float:
        base_score = super().score(metrics)
        shrink_score = abs(metrics.volume_shrink_pct or 0)
        return round(base_score + shrink_score, 4)


class HalfYearBottomConsolidationStrategy(BaseStrategy):
    name = "half_year_bottom_consolidation"
    description = "近120个交易日价格位于半年底部区域并低位盘整的股票"
    days = 120
    recent_days = 40
    max_recent_amplitude_pct = 22.0
    max_recent_abs_trend_pct = 8.0
    max_close_position_pct = 35.0
    max_recent_mid_position_pct = 40.0

    def run(self, context: StrategyContext) -> list[StrategyMatch]:
        matches: list[StrategyMatch] = []
        for ts_code, rows in context.recent_daily_rows_by_code(self.days).items():
            half_year_metrics = compact_box_metrics(rows, self.days)
            recent_metrics = compact_box_metrics(rows, self.recent_days)
            if not half_year_metrics or not recent_metrics:
                continue

            recent_mid_price = (
                recent_metrics.high + recent_metrics.low
            ) / 2
            recent_mid_position_pct = (
                (recent_mid_price - half_year_metrics.low)
                / (half_year_metrics.high - half_year_metrics.low)
                * 100
            )

            if (
                half_year_metrics.close_position_pct <= self.max_close_position_pct
                and recent_mid_position_pct <= self.max_recent_mid_position_pct
                and recent_metrics.amplitude_pct <= self.max_recent_amplitude_pct
                and abs(recent_metrics.trend_pct) <= self.max_recent_abs_trend_pct
            ):
                data = half_year_metrics.as_data()
                data.update(
                    {
                        "recent_days": self.recent_days,
                        "recent_amplitude_pct": round(
                            recent_metrics.amplitude_pct,
                            2,
                        ),
                        "recent_trend_pct": round(recent_metrics.trend_pct, 2),
                        "recent_mid_position_pct": round(
                            recent_mid_position_pct,
                            2,
                        ),
                    }
                )
                matches.append(
                    StrategyMatch(
                        ts_code=ts_code,
                        reason=(
                            f"半年价格位置={half_year_metrics.close_position_pct:.2f}%, "
                            f"近{self.recent_days}日振幅={recent_metrics.amplitude_pct:.2f}%"
                        ),
                        score=self.score(
                            half_year_metrics,
                            recent_metrics,
                            recent_mid_position_pct,
                        ),
                        data=data,
                    )
                )
        return matches

    def score(
        self,
        half_year_metrics: DailyMetrics,
        recent_metrics: DailyMetrics,
        recent_mid_position_pct: float,
    ) -> float:
        bottom_score = max(0.0, self.max_close_position_pct - half_year_metrics.close_position_pct)
        compact_score = max(0.0, self.max_recent_amplitude_pct - recent_metrics.amplitude_pct)
        mid_score = max(0.0, self.max_recent_mid_position_pct - recent_mid_position_pct)
        return round(bottom_score + compact_score + mid_score, 4)
