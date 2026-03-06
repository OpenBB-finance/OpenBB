"""Example user algorithm wired into the trading runtime."""

from __future__ import annotations

import pandas as pd

from openbb_quant_ml.service.trading.custom_algorithm_adapter import BaseCustomAlgorithm
from openbb_quant_ml.service.trading.indicator_engine import compute_indicator_frame


class SampleMomentumAlgorithm(BaseCustomAlgorithm):
    name = "sample_momentum"
    version = "0.1.0"
    description = "Example custom algorithm that reacts to EMA trend and RSI recovery."
    parameters = {"rsi_floor": 45.0}
    warmup_period = 80

    def generate_features(self, data: pd.DataFrame) -> pd.DataFrame:
        return compute_indicator_frame(data)

    def generate_signal(self, data: pd.DataFrame):
        if data.empty or len(data) < 3:
            return pd.DataFrame()
        current = data.iloc[-1]
        previous = data.iloc[-2]
        if current["ema_fast"] > current["ema_slow"] and previous["rsi"] < self.parameters["rsi_floor"] <= current["rsi"]:
            return pd.DataFrame(
                [
                    {
                        "timestamp": pd.Timestamp(current["date"]).isoformat(),
                        "ticker": str(current.get("symbol", "")),
                        "signal": "entry",
                        "signal_type": "entry",
                        "side": "buy",
                        "strength": 0.62,
                        "confidence": 0.57,
                        "reason": "사용자 알고리즘 예시: EMA 추세 유지 + RSI 회복",
                        "metadata": {
                            "price": float(current["close"]),
                            "rsi": float(current["rsi"]),
                            "macd_hist": float(current["macd_hist"]),
                            "ma_relation": float(current["ma_relation"]),
                            "volume_change_pct": float(current["volume_change_pct"]),
                            "atr": float(current["atr"]),
                            "recent_return": float(current["recent_return"]),
                            "recommended_action": "Buy",
                        },
                    }
                ]
            )
        return pd.DataFrame()


ALGORITHM = SampleMomentumAlgorithm()
