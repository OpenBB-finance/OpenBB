"""Cboe options strategy pricing models."""

from __future__ import annotations

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from pydantic import Field

PERCENT = {"x-unit_measurement": "percent"}


class StrategyData(Data):
    """Long straddle / strangle pricing at one expiration."""

    __alias_dict__ = {
        "expiration": "Expiration",
        "dte": "DTE",
        "underlying_price": "Underlying Price",
        "strike_1": "Strike 1",
        "strike_2": "Strike 2",
        "strike_1_premium": "Strike 1 Premium",
        "strike_2_premium": "Strike 2 Premium",
        "cost": "Cost",
        "cost_percent": "Cost Percent",
        "breakeven_upper": "Breakeven Upper",
        "breakeven_upper_percent": "Breakeven Upper Percent",
        "breakeven_lower": "Breakeven Lower",
        "breakeven_lower_percent": "Breakeven Lower Percent",
        "max_profit": "Max Profit",
        "max_loss": "Max Loss",
    }

    expiration: dateType = Field(title="Expiry")
    dte: int = Field(title="DTE")
    strike_1: int | float = Field(title="Call Strike")
    strike_2: int | float = Field(title="Put Strike")
    underlying_price: float = Field(title="Underlying Price")
    cost_percent: float = Field(title="Cost %", json_schema_extra=PERCENT)
    max_profit: float | None = Field(default=None, title="Max Profit")
    max_loss: float | None = Field(
        default=None, title="Max Loss", json_schema_extra=PERCENT
    )
    breakeven_upper: float = Field(title="Breakeven Upper")
    breakeven_upper_percent: float = Field(
        title="Breakeven Upper %", json_schema_extra=PERCENT
    )
    breakeven_lower: float = Field(title="Breakeven Lower")
    breakeven_lower_percent: float = Field(
        title="Breakeven Lower %", json_schema_extra=PERCENT
    )
    strike_1_premium: float = Field(title="Call Premium")
    strike_2_premium: float = Field(title="Put Premium")
    cost: float = Field(title="Cost")


class SpreadData(Data):
    """Vertical (bull/bear) spread pricing at one expiration."""

    __alias_dict__ = {
        "strategy": "Strategy",
        "expiration": "Expiration",
        "dte": "DTE",
        "underlying_price": "Underlying Price",
        "sold_strike": "Strike 1",
        "bought_strike": "Strike 2",
        "sold_premium": "Strike 1 Premium",
        "bought_premium": "Strike 2 Premium",
        "cost": "Cost",
        "cost_percent": "Cost Percent",
        "breakeven_lower": "Breakeven Lower",
        "breakeven_lower_percent": "Breakeven Lower Percent",
        "breakeven_upper": "Breakeven Upper",
        "breakeven_upper_percent": "Breakeven Upper Percent",
        "max_profit": "Max Profit",
        "max_loss": "Max Loss",
    }

    strategy: str = Field(title="Strategy")
    expiration: dateType = Field(title="Expiry")
    dte: int = Field(title="DTE")
    sold_strike: float = Field(title="Short Strike")
    bought_strike: float = Field(title="Long Strike")
    underlying_price: float = Field(title="Underlying Price")
    cost: float = Field(title="Cost")
    cost_percent: float = Field(title="Cost %", json_schema_extra=PERCENT)
    max_profit: float | None = Field(default=None, title="Max Profit")
    max_loss: float | None = Field(default=None, title="Max Loss")
    breakeven_lower: float | None = Field(default=None, title="Breakeven Lower")
    breakeven_lower_percent: float | None = Field(
        default=None, title="Breakeven Lower %", json_schema_extra=PERCENT
    )
    breakeven_upper: float | None = Field(default=None, title="Breakeven Upper")
    breakeven_upper_percent: float | None = Field(
        default=None, title="Breakeven Upper %", json_schema_extra=PERCENT
    )
    sold_premium: float = Field(title="Short Premium")
    bought_premium: float = Field(title="Long Premium")


def to_strategies(df) -> list[StrategyData]:
    """Convert a ``strategies()`` frame to ``StrategyData`` rows.

    Parameters
    ----------
    df : DataFrame
        The frame returned by ``OptionsChainsData.strategies``.

    Returns
    -------
    list[StrategyData]
        One row per expiration.
    """
    from numpy import inf, nan

    df = df.drop(columns=[c for c in ("Strategy", "Payoff Ratio") if c in df.columns])

    return [
        StrategyData.model_validate(d)
        for d in df.replace({nan: None, inf: None, -inf: None}).to_dict("records")
    ]


def to_spreads(df) -> list[SpreadData]:
    """Convert a vertical-spread frame to ``SpreadData`` rows.

    Parameters
    ----------
    df : DataFrame
        The frame returned by ``OptionsChainsData.strategies``.

    Returns
    -------
    list[SpreadData]
        One row per spread and expiration.
    """
    from numpy import inf, nan

    df = df.drop(columns=[c for c in ("Payoff Ratio",) if c in df.columns])

    return [
        SpreadData.model_validate(d)
        for d in df.replace({nan: None, inf: None, -inf: None}).to_dict("records")
    ]
