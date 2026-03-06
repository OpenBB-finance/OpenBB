"""Built-in trading strategies and registry."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import pandas as pd

from openbb_quant_ml.service.trading.indicator_engine import compute_indicator_frame


@dataclass
class BaseTradingStrategy(ABC):
    """Base class for built-in technical strategies."""

    name: str
    version: str
    description: str
    required_columns: tuple[str, ...] = ("date", "open", "high", "low", "close", "volume")
    warmup_period: int = 60

    @abstractmethod
    def generate_signal(
        self,
        data: pd.DataFrame,
        *,
        params: dict[str, Any],
        symbol: str,
    ) -> dict[str, Any] | None:
        """Generate one normalized signal row from symbol data."""

    @abstractmethod
    def explain_signal(self, row: dict[str, Any]) -> str:
        """Return a human-readable explanation for the signal."""

    def should_enter(self, row: dict[str, Any], has_position: bool) -> bool:
        return str(row.get("signal_type", "")) == "entry" and not has_position

    def should_exit(self, row: dict[str, Any], has_position: bool) -> bool:
        return str(row.get("signal_type", "")) == "exit" and has_position


def _signal_template(
    *,
    strategy: BaseTradingStrategy,
    symbol: str,
    row: pd.Series,
    signal_type: str,
    side: str,
    strength: float,
    confidence: float,
    reason: str,
) -> dict[str, Any]:
    recommended_action = (
        "Buy"
        if side == "buy" and signal_type == "entry"
        else "Sell"
        if side == "sell" and signal_type == "exit"
        else "Hold"
    )
    return {
        "signal_id": f"{strategy.name}:{symbol}:{pd.Timestamp(row['date']).isoformat()}:{signal_type}",
        "timestamp": pd.Timestamp(row["date"]).isoformat(),
        "ticker": symbol,
        "signal": signal_type,
        "signal_type": signal_type,
        "side": side,
        "strength": float(max(0.0, min(1.0, strength))),
        "confidence": float(max(0.0, min(1.0, confidence))),
        "strategy_name": strategy.name,
        "algorithm_version": strategy.version,
        "entry_price_hint": float(row.get("close", 0.0) or 0.0),
        "stop_loss_hint": None,
        "take_profit_hint": None,
        "reason": reason,
        "metadata": {
            "price": float(row.get("close", 0.0) or 0.0),
            "rsi": float(row.get("rsi", 0.0) or 0.0),
            "macd_hist": float(row.get("macd_hist", 0.0) or 0.0),
            "ma_relation": float(row.get("ma_relation", 0.0) or 0.0),
            "volume_change_pct": float(row.get("volume_change_pct", 0.0) or 0.0),
            "atr": float(row.get("atr", 0.0) or 0.0),
            "recent_return": float(row.get("recent_return", 0.0) or 0.0),
            "recommended_action": recommended_action,
        },
    }


class EMACrossStrategy(BaseTradingStrategy):
    def __init__(self) -> None:
        super().__init__(
            name="ema_cross",
            version="1.0.0",
            description="Fast EMA cross with RSI ceiling filter.",
            warmup_period=80,
        )

    def generate_signal(
        self,
        data: pd.DataFrame,
        *,
        params: dict[str, Any],
        symbol: str,
    ) -> dict[str, Any] | None:
        enriched = compute_indicator_frame(
            data,
            ema_fast=int(params.get("fast_span", 12) or 12),
            ema_slow=int(params.get("slow_span", 26) or 26),
        )
        if len(enriched) < 3:
            return None
        current = enriched.iloc[-1]
        previous = enriched.iloc[-2]
        rsi_ceiling = float(params.get("rsi_ceiling", 72.0) or 72.0)
        crossed_up = previous["ema_fast"] <= previous["ema_slow"] and current["ema_fast"] > current["ema_slow"]
        crossed_down = previous["ema_fast"] >= previous["ema_slow"] and current["ema_fast"] < current["ema_slow"]
        if crossed_up and float(current.get("rsi", 50.0) or 50.0) <= rsi_ceiling:
            return _signal_template(
                strategy=self,
                symbol=symbol,
                row=current,
                signal_type="entry",
                side="buy",
                strength=0.7,
                confidence=0.68,
                reason="단기 EMA가 장기 EMA를 상향 돌파했고 RSI 과열 구간이 아닙니다.",
            )
        if crossed_down:
            return _signal_template(
                strategy=self,
                symbol=symbol,
                row=current,
                signal_type="exit",
                side="sell",
                strength=0.65,
                confidence=0.64,
                reason="단기 EMA가 장기 EMA를 하향 돌파했습니다.",
            )
        return None

    def explain_signal(self, row: dict[str, Any]) -> str:
        return str(row.get("reason", "EMA cross signal"))


class RSIReversalStrategy(BaseTradingStrategy):
    def __init__(self) -> None:
        super().__init__(
            name="rsi_reversal",
            version="1.0.0",
            description="Oversold RSI reversal for long entries.",
            warmup_period=40,
        )

    def generate_signal(
        self,
        data: pd.DataFrame,
        *,
        params: dict[str, Any],
        symbol: str,
    ) -> dict[str, Any] | None:
        enriched = compute_indicator_frame(data)
        if len(enriched) < 3:
            return None
        current = enriched.iloc[-1]
        previous = enriched.iloc[-2]
        oversold = float(params.get("oversold", 30.0) or 30.0)
        rebound_level = float(params.get("rebound_level", 35.0) or 35.0)
        overbought_exit = float(params.get("overbought_exit", 70.0) or 70.0)
        if previous["rsi"] < oversold and current["rsi"] >= rebound_level and current["close"] > previous["close"]:
            return _signal_template(
                strategy=self,
                symbol=symbol,
                row=current,
                signal_type="entry",
                side="buy",
                strength=0.75,
                confidence=0.7,
                reason="RSI가 과매도 구간 이탈 후 반등했고 가격이 동반 상승했습니다.",
            )
        if previous["rsi"] >= overbought_exit and current["rsi"] < previous["rsi"] and current["close"] < previous["close"]:
            return _signal_template(
                strategy=self,
                symbol=symbol,
                row=current,
                signal_type="exit",
                side="sell",
                strength=0.6,
                confidence=0.58,
                reason="RSI 과열 완화와 가격 약화가 동시에 발생했습니다.",
            )
        return None

    def explain_signal(self, row: dict[str, Any]) -> str:
        return str(row.get("reason", "RSI reversal signal"))


class BreakoutVolumeStrategy(BaseTradingStrategy):
    def __init__(self) -> None:
        super().__init__(
            name="breakout_volume",
            version="1.0.0",
            description="Breakout with volume expansion and ATR filter.",
            warmup_period=80,
        )

    def generate_signal(
        self,
        data: pd.DataFrame,
        *,
        params: dict[str, Any],
        symbol: str,
    ) -> dict[str, Any] | None:
        lookback = int(params.get("lookback", 20) or 20)
        enriched = compute_indicator_frame(data, breakout_lookback=lookback)
        if len(enriched) < max(lookback + 2, 30):
            return None
        current = enriched.iloc[-1]
        previous = enriched.iloc[-2]
        volume_multiple = float(params.get("volume_multiple", 1.8) or 1.8)
        min_atr_pct = float(params.get("min_atr_pct", 0.01) or 0.01)
        max_atr_pct = float(params.get("max_atr_pct", 0.10) or 0.10)
        atr_pct = float(current.get("atr_pct", 0.0) or 0.0)
        broke_out = float(current.get("close", 0.0) or 0.0) > float(current.get("rolling_high_breakout", 0.0) or 0.0)
        volume_ok = float(current.get("volume", 0.0) or 0.0) >= float(current.get("volume_avg", 0.0) or 0.0) * volume_multiple
        atr_ok = min_atr_pct <= atr_pct <= max_atr_pct
        if broke_out and volume_ok and atr_ok:
            return _signal_template(
                strategy=self,
                symbol=symbol,
                row=current,
                signal_type="entry",
                side="buy",
                strength=0.8,
                confidence=0.74,
                reason="최근 고점 돌파와 거래량 급증이 확인됐고 ATR 변동성 필터를 통과했습니다.",
            )
        exit_break = float(current.get("close", 0.0) or 0.0) < float(current.get("rolling_low_exit", 0.0) or 0.0)
        if previous["close"] >= previous.get("rolling_low_exit", previous["close"]) and exit_break:
            return _signal_template(
                strategy=self,
                symbol=symbol,
                row=current,
                signal_type="exit",
                side="sell",
                strength=0.62,
                confidence=0.6,
                reason="브레이크아웃 실패로 최근 지지선 아래로 이탈했습니다.",
            )
        return None

    def explain_signal(self, row: dict[str, Any]) -> str:
        return str(row.get("reason", "Breakout-volume signal"))


def get_builtin_strategy_registry() -> dict[str, BaseTradingStrategy]:
    """Return the built-in trading strategy registry."""
    strategies: list[BaseTradingStrategy] = [
        EMACrossStrategy(),
        RSIReversalStrategy(),
        BreakoutVolumeStrategy(),
    ]
    return {item.name: item for item in strategies}
