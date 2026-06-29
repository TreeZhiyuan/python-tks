from __future__ import annotations

from dataclasses import dataclass
from statistics import fmean, pstdev
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


@dataclass(frozen=True)
class SidewaysMetrics:
    ts_code: str
    days: int
    latest_trade_date: str
    latest_close: float
    high: float
    low: float
    mean_close: float
    sideways_score: float
    platform_score: float
    total_score: float
    slope_ratio_pct: float
    regression_error_pct: float
    box_ratio_pct: float
    cv_pct: float
    atr_pct: float
    boll_width_pct: float
    ma_spread_pct: float
    distance_to_high_pct: float
    volume_shrink_ratio_pct: float | None
    history_days: int
    long_gain_pct: float
    long_ma_trend_pct: float | None
    slope_score: float
    error_score: float
    box_score: float
    atr_score: float
    boll_score: float
    cv_score: float
    ma_score: float
    distance_to_high_score: float
    volume_contraction_score: float
    long_trend_score: float

    def as_data(self) -> dict[str, Any]:
        return {
            "days": self.days,
            "latest_trade_date": self.latest_trade_date,
            "latest_close": round(self.latest_close, 4),
            "high": round(self.high, 4),
            "low": round(self.low, 4),
            "mean_close": round(self.mean_close, 4),
            "sideways_score": round(self.sideways_score, 2),
            "platform_score": round(self.platform_score, 2),
            "total_score": round(self.total_score, 2),
            "slope_ratio_pct": round(self.slope_ratio_pct, 4),
            "regression_error_pct": round(self.regression_error_pct, 2),
            "box_ratio_pct": round(self.box_ratio_pct, 2),
            "cv_pct": round(self.cv_pct, 2),
            "atr_pct": round(self.atr_pct, 2),
            "boll_width_pct": round(self.boll_width_pct, 2),
            "ma_spread_pct": round(self.ma_spread_pct, 2),
            "distance_to_high_pct": round(self.distance_to_high_pct, 2),
            "volume_shrink_ratio_pct": (
                round(self.volume_shrink_ratio_pct, 2)
                if self.volume_shrink_ratio_pct is not None
                else None
            ),
            "history_days": self.history_days,
            "long_gain_pct": round(self.long_gain_pct, 2),
            "long_ma_trend_pct": (
                round(self.long_ma_trend_pct, 2)
                if self.long_ma_trend_pct is not None
                else None
            ),
            "sub_scores": {
                "slope": round(self.slope_score, 2),
                "regression_error": round(self.error_score, 2),
                "box": round(self.box_score, 2),
                "atr": round(self.atr_score, 2),
                "boll": round(self.boll_score, 2),
                "cv": round(self.cv_score, 2),
                "ma_spread": round(self.ma_score, 2),
                "distance_to_high": round(self.distance_to_high_score, 2),
                "volume_contraction": round(self.volume_contraction_score, 2),
                "long_trend": round(self.long_trend_score, 2),
            },
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


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def ratio_score(value_pct: float, excellent_pct: float, poor_pct: float) -> float:
    if value_pct <= excellent_pct:
        return 100.0
    if value_pct >= poor_pct:
        return 0.0
    return (poor_pct - value_pct) / (poor_pct - excellent_pct) * 100


def linear_regression(values: list[float]) -> tuple[float, float, list[float]]:
    count = len(values)
    if count == 0:
        return 0.0, 0.0, []

    x_values = list(range(count))
    x_mean = fmean(x_values)
    y_mean = fmean(values)
    denominator = sum((x - x_mean) ** 2 for x in x_values)
    slope = (
        sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values)) / denominator
        if denominator > 0
        else 0.0
    )
    intercept = y_mean - slope * x_mean
    fitted = [slope * x + intercept for x in x_values]
    return slope, intercept, fitted


def moving_average(values: list[float], days: int) -> float | None:
    if len(values) < days:
        return None
    return fmean(values[-days:])


def average_true_range_pct(rows: list[dict[str, Any]], days: int = 14) -> float | None:
    if len(rows) < days + 1:
        return None

    true_ranges: list[float] = []
    for index in range(len(rows) - days, len(rows)):
        row = rows[index]
        previous_close = rows[index - 1].get("close_price")
        high = row.get("high_price")
        low = row.get("low_price")
        close = row.get("close_price")
        try:
            high_value = float(high)
            low_value = float(low)
            close_value = float(close)
            previous_close_value = float(previous_close)
        except (TypeError, ValueError):
            return None
        true_ranges.append(
            max(
                high_value - low_value,
                abs(high_value - previous_close_value),
                abs(low_value - previous_close_value),
            )
        )

    latest_close = float(rows[-1]["close_price"])
    if latest_close <= 0:
        return None
    return fmean(true_ranges) / latest_close * 100


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


class BottomBoxConsolidationStrategy(BaseStrategy):
    name = "bottom_box_consolidation"
    description = "线性回归综合评分识别近60日平台整理且长期趋势不弱的股票"
    days = 250
    sideways_days = 60
    min_history_days = 80
    min_sideways_score = 50.0
    min_long_gain_pct = 10.0
    min_long_ma_trend_pct = 0.0
    max_distance_to_high_pct = 10.0
    max_volume_shrink_ratio_pct = 125.0
    max_box_ratio_pct = 24.0

    def run(self, context: StrategyContext) -> list[StrategyMatch]:
        matches: list[StrategyMatch] = []
        daily_rows_by_code = context.recent_daily_rows_by_code(self.days)

        for ts_code, daily_rows in daily_rows_by_code.items():
            metrics = self.sideways_metrics(daily_rows)
            if not metrics:
                continue

            if self.is_match(metrics):
                matches.append(
                    StrategyMatch(
                        ts_code=ts_code,
                        reason=(
                            f"横盘得分={metrics.sideways_score:.2f}, "
                            f"平台得分={metrics.platform_score:.2f}, "
                            f"箱体高度={metrics.box_ratio_pct:.2f}%, "
                            f"距{self.sideways_days}日高点={metrics.distance_to_high_pct:.2f}%"
                        ),
                        score=metrics.total_score,
                        data=metrics.as_data(),
                    )
                )
        return matches

    def is_match(self, metrics: SidewaysMetrics) -> bool:
        volume_ok = (
            metrics.volume_shrink_ratio_pct is not None
            and metrics.volume_shrink_ratio_pct <= self.max_volume_shrink_ratio_pct
        )
        long_trend_ok = metrics.long_gain_pct >= self.min_long_gain_pct or (
            metrics.long_ma_trend_pct is not None
            and metrics.long_ma_trend_pct > self.min_long_ma_trend_pct
        )
        return (
            metrics.sideways_score >= self.min_sideways_score
            and metrics.box_ratio_pct <= self.max_box_ratio_pct
            and metrics.distance_to_high_pct <= self.max_distance_to_high_pct
            and volume_ok
            and long_trend_ok
        )

    def sideways_metrics(self, rows: list[dict[str, Any]]) -> SidewaysMetrics | None:
        if len(rows) < self.min_history_days:
            return None

        window = rows[-self.sideways_days :]
        if len(window) < self.sideways_days:
            return None

        close_prices = numeric_values(row.get("close_price") for row in window)
        high_prices = numeric_values(row.get("high_price") for row in window)
        low_prices = numeric_values(row.get("low_price") for row in window)
        volumes = numeric_values(row.get("vol") for row in window)
        if (
            len(close_prices) < self.sideways_days
            or len(high_prices) < self.sideways_days
            or len(low_prices) < self.sideways_days
            or len(volumes) < 60
        ):
            return None

        latest_close = close_prices[-1]
        mean_close = fmean(close_prices)
        if latest_close < MIN_CLOSE_PRICE or mean_close <= 0:
            return None

        high = max(high_prices)
        low = min(low_prices)
        if low <= 0 or high <= low:
            return None

        slope, _, fitted = linear_regression(close_prices)
        residuals = [price - fit for price, fit in zip(close_prices, fitted)]
        regression_error_pct = pstdev(residuals) / mean_close * 100 if len(residuals) > 1 else 0.0
        slope_ratio_pct = abs(slope) / mean_close * 100
        box_ratio_pct = (high - low) / mean_close * 100
        cv_pct = pstdev(close_prices) / mean_close * 100 if len(close_prices) > 1 else 0.0
        atr_pct = average_true_range_pct(window) or 0.0
        boll_width_pct = cv_pct * 4

        ma_values = [
            ma
            for ma in (
                moving_average(close_prices, 5),
                moving_average(close_prices, 10),
                moving_average(close_prices, 20),
                moving_average(close_prices, 60),
            )
            if ma is not None
        ]
        ma_spread_pct = (
            (max(ma_values) - min(ma_values)) / mean_close * 100
            if len(ma_values) >= 2
            else 0.0
        )

        latest_vol_avg = fmean(volumes[-20:])
        previous_vol_avg = fmean(volumes[-60:])
        volume_shrink_ratio_pct = (
            latest_vol_avg / previous_vol_avg * 100 if previous_vol_avg > 0 else None
        )
        distance_to_high_pct = (high - latest_close) / high * 100

        history_closes = numeric_values(row.get("close_price") for row in rows)
        if len(history_closes) < self.min_history_days:
            return None
        long_gain_pct = (
            (history_closes[-1] / history_closes[0] - 1) * 100
            if history_closes[0] > 0
            else 0.0
        )

        long_ma_trend_pct: float | None = None
        if len(history_closes) >= 120:
            first_ma = fmean(history_closes[:60])
            last_ma = fmean(history_closes[-60:])
            long_ma_trend_pct = (last_ma / first_ma - 1) * 100 if first_ma > 0 else None

        slope_score = ratio_score(slope_ratio_pct, 0.02, 0.15)
        error_score = ratio_score(regression_error_pct, 2.0, 6.0)
        box_score = ratio_score(box_ratio_pct, 12.0, 28.0)
        atr_score = ratio_score(atr_pct, 1.5, 4.0)
        boll_score = ratio_score(boll_width_pct, 8.0, 20.0)
        cv_score = ratio_score(cv_pct, 2.0, 6.0)
        ma_score = ratio_score(ma_spread_pct, 1.0, 5.0)

        sideways_score = (
            slope_score * 0.25
            + error_score * 0.20
            + box_score * 0.20
            + atr_score * 0.10
            + boll_score * 0.10
            + cv_score * 0.10
            + ma_score * 0.05
        )
        distance_to_high_score = ratio_score(distance_to_high_pct, 2.0, 12.0)
        volume_contraction_score = (
            ratio_score(volume_shrink_ratio_pct, 60.0, 110.0)
            if volume_shrink_ratio_pct is not None
            else 0.0
        )
        long_gain_score = clamp(long_gain_pct / self.min_long_gain_pct * 100)
        long_ma_score = (
            clamp((long_ma_trend_pct or 0.0) / 20.0 * 100)
            if long_ma_trend_pct is not None
            else 0.0
        )
        long_trend_score = max(long_gain_score, long_ma_score)
        platform_score = (
            distance_to_high_score * 0.35
            + volume_contraction_score * 0.25
            + long_trend_score * 0.40
        )
        total_score = sideways_score * 0.70 + platform_score * 0.30

        return SidewaysMetrics(
            ts_code=str(window[-1]["ts_code"]),
            days=self.sideways_days,
            latest_trade_date=str(window[-1]["trade_date"]),
            latest_close=latest_close,
            high=high,
            low=low,
            mean_close=mean_close,
            sideways_score=round(sideways_score, 4),
            platform_score=round(platform_score, 4),
            total_score=round(total_score, 4),
            slope_ratio_pct=slope_ratio_pct,
            regression_error_pct=regression_error_pct,
            box_ratio_pct=box_ratio_pct,
            cv_pct=cv_pct,
            atr_pct=atr_pct,
            boll_width_pct=boll_width_pct,
            ma_spread_pct=ma_spread_pct,
            distance_to_high_pct=distance_to_high_pct,
            volume_shrink_ratio_pct=volume_shrink_ratio_pct,
            history_days=len(history_closes),
            long_gain_pct=long_gain_pct,
            long_ma_trend_pct=long_ma_trend_pct,
            slope_score=slope_score,
            error_score=error_score,
            box_score=box_score,
            atr_score=atr_score,
            boll_score=boll_score,
            cv_score=cv_score,
            ma_score=ma_score,
            distance_to_high_score=distance_to_high_score,
            volume_contraction_score=volume_contraction_score,
            long_trend_score=long_trend_score,
        )
