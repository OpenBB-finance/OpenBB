"""Indicator-based screening across a basket of symbols."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Literal

from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.app.utils import basemodel_to_df, df_to_basemodel
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

from openbb_technical.multi.compose import (
    _call_indicator,
    _resolve_indicator,
    _to_records,
)

# Bare 'date' alias for function signatures so the static-package builder
# writes 'date' (which it imports from datetime) rather than 'dateType' which it does not.
date = dateType


router = Router(prefix="", description="Indicator-based screening.")


Operator = Literal[
    "gt",
    "gte",
    "lt",
    "lte",
    "eq",
    "between",
    "crossed_above",
    "crossed_below",
    "made_high",
    "made_low",
]


class ScreenCondition(QueryParams):
    """Describe one screening predicate over a single indicator output column.

    Parameters
    ----------
    indicator : str
        Indicator endpoint name, e.g. ``rsi`` or ``macd``.
    column : str
        Column to read from the indicator's output, e.g. ``close_RSI_14``. The
        column name is matched case-insensitively against the indicator's
        emitted columns.
    operator : Operator
        Comparison or event operator. Scalar comparisons (``gt``, ``gte``,
        ``lt``, ``lte``, ``eq``) take a single threshold; ``between`` takes a
        ``(low, high)`` tuple; event operators (``crossed_above``,
        ``crossed_below``, ``made_high``, ``made_low``) take a
        ``(threshold, lookback_bars)`` tuple.
    value : float | tuple[float, float]
        Operator argument — a scalar threshold or a two-element tuple
        depending on ``operator`` (see above).
    indicator_params : dict[str, float | int | str], optional
        Keyword arguments forwarded to the indicator endpoint. Empty by
        default.
    """

    indicator: str = Field(description="Indicator endpoint name, e.g. ``rsi``.")
    column: str = Field(
        description=(
            "Column to read from the indicator's output, e.g. "
            "``close_RSI_14``. The column name is matched case-insensitively."
        ),
    )
    operator: Operator = Field(description="Comparison or event operator.")
    value: float | tuple[float, float] = Field(
        description=(
            "Threshold for comparison operators, ``(low, high)`` tuple for "
            "``between``, or ``(threshold, lookback_bars)`` tuple for event "
            "operators (``crossed_*``/``made_*``)."
        ),
    )
    indicator_params: dict[str, float | int | str] = Field(
        default_factory=dict,
        description="Keyword arguments forwarded to the indicator endpoint.",
    )


class ScreenQueryParams(QueryParams):
    """Query parameters for the multi-symbol screen endpoint.

    Parameters
    ----------
    data : list[Data]
        Long-format multi-symbol data with a ``symbol`` column. Every group
        is evaluated independently.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    target : str, optional
        Default target column forwarded to indicators that accept one, by
        default ``"close"``.
    conditions : list[ScreenCondition]
        Predicates to evaluate against each symbol's computed indicators.
    combine : {"and", "or"}, optional
        ``"and"`` (default) returns symbols matching every condition;
        ``"or"`` returns symbols matching at least one condition.
    as_of_date : date | str, optional
        Anchor date for evaluation. ``None`` (default) uses each symbol's
        most recent row.
    """

    __category__ = "multi"
    __output_columns__ = ("symbol", "as_of_date", "matched_conditions", "values")

    data: list[Data] = Field(
        description="Long-format multi-symbol data with a ``symbol`` column.",
    )
    index: str = Field(default="date", description="Index column name in ``data``.")
    target: str = Field(default="close", description="Default target column.")
    conditions: list[ScreenCondition] = Field(
        description="Predicates to evaluate against each symbol's indicators.",
    )
    combine: Literal["and", "or"] = Field(
        default="and",
        description=(
            "``and`` returns symbols matching every condition; ``or`` returns "
            "symbols matching at least one."
        ),
    )
    as_of_date: datetime | dateType | str | None = Field(
        default=None,
        description=("Anchor date. Defaults to the latest date per symbol when unset."),
    )


class ScreenMatch(Data):
    """One screened symbol that satisfied the configured conditions.

    Parameters
    ----------
    symbol : str
        Symbol that matched.
    as_of_date : date | str
        Date used to evaluate the predicates for this symbol.
    matched_conditions : int
        Number of conditions that fired for this symbol.
    values : dict[str, float]
        Latest indicator values that contributed to the match, keyed as
        ``"<indicator>.<column>"``.
    """

    symbol: str = Field(description="Symbol that matched.")
    as_of_date: datetime | dateType | str = Field(
        description="Date used for evaluation."
    )
    matched_conditions: int = Field(description="How many conditions fired.")
    values: dict[str, float] = Field(
        description=(
            "Latest indicator values that contributed to the match, keyed by "
            '``"<indicator>.<column>"``.'
        ),
    )


_EVENT_OPS = {"crossed_above", "crossed_below", "made_high", "made_low"}


def _normalise_value(value: Any) -> tuple[float, float] | float:
    """Coerce list-style inputs to tuples for the tuple-valued operators."""
    if isinstance(value, list):
        if len(value) != 2:  # pragma: no cover - schema validates length
            raise ValueError("Tuple-valued conditions require exactly two elements.")
        return (float(value[0]), float(value[1]))
    if isinstance(value, tuple):
        return (float(value[0]), float(value[1]))
    return float(value)


def _find_column(row: dict[str, Any], column: str) -> str | None:
    """Case-insensitive lookup for the requested indicator column."""
    if column in row:
        return column
    lowered = column.lower()
    for key in row:
        if isinstance(key, str) and key.lower() == lowered:
            return key
    return None


def _evaluate(
    series: list[tuple[Any, float | None]],
    operator: Operator,
    value: tuple[float, float] | float,
    anchor_index: int,
) -> tuple[bool, float | None]:
    """Run ``operator`` against the indicator series at ``anchor_index``."""
    if anchor_index < 0 or anchor_index >= len(series):
        return False, None  # pragma: no cover - defensive
    _, latest = series[anchor_index]
    if latest is None:
        return False, None

    if operator == "gt":
        return latest > float(value), latest  # ty: ignore[invalid-argument-type]
    if operator == "gte":
        return latest >= float(value), latest  # ty: ignore[invalid-argument-type]
    if operator == "lt":
        return latest < float(value), latest  # ty: ignore[invalid-argument-type]
    if operator == "lte":
        return latest <= float(value), latest  # ty: ignore[invalid-argument-type]
    if operator == "eq":
        return latest == float(value), latest  # ty: ignore[invalid-argument-type]
    if operator == "between":
        low, high = value  # ty: ignore[not-iterable]
        return low <= latest <= high, latest

    threshold, lookback_raw = value  # ty: ignore[not-iterable]
    lookback = int(lookback_raw)
    start = max(0, anchor_index - lookback + 1)
    window = [v for _, v in series[start : anchor_index + 1] if v is not None]
    if len(window) < 2:
        return False, latest

    if operator == "crossed_above":
        fired = any(
            a <= threshold < b for a, b in zip(window[:-1], window[1:], strict=False)
        )
        return fired, latest
    if operator == "crossed_below":
        fired = any(
            a >= threshold > b for a, b in zip(window[:-1], window[1:], strict=False)
        )
        return fired, latest
    if operator == "made_high":
        fired = latest >= max(window)
        return fired, latest
    fired = latest <= min(window)
    return fired, latest


@router.command(methods=["POST"])
def screen(params: ScreenQueryParams) -> OBBject[list[ScreenMatch]]:
    """Filter a multi-symbol basket by indicator-driven conditions."""

    import pandas as pd

    df = basemodel_to_df(params.data, index=params.index)
    if "symbol" not in df.columns:
        raise ValueError("Input data must contain a 'symbol' column.")

    anchor: Any | None
    if params.as_of_date is None:
        anchor = None
    else:
        anchor_ts = pd.to_datetime(params.as_of_date)
        anchor = anchor_ts.date() if hasattr(anchor_ts, "date") else anchor_ts

    matches: list[ScreenMatch] = []

    for symbol, group in df.groupby("symbol"):
        symbol_df = group.drop(columns=["symbol"]).copy()
        if symbol_df.empty:
            continue  # pragma: no cover - groupby never yields empty groups
        if anchor is not None:
            mask = [idx_val <= anchor for idx_val in symbol_df.index]
            symbol_df = symbol_df.loc[mask]
            if symbol_df.empty:
                continue
        symbol_records = df_to_basemodel(symbol_df.reset_index())

        fired_count = 0
        captured: dict[str, float] = {}
        any_skipped = False

        for condition in params.conditions:
            fn = _resolve_indicator(condition.indicator)
            if fn is None:
                any_skipped = True
                continue
            indicator_result = _call_indicator(
                fn,
                data=symbol_records,
                index=params.index,
                target=params.target,
                **condition.indicator_params,
            )
            rows = _to_records(indicator_result)
            if not rows:
                continue  # pragma: no cover - indicator returned nothing
            col_name = _find_column(rows[0], condition.column)
            if col_name is None:
                continue
            series = [(row.get(params.index), row.get(col_name)) for row in rows]
            anchor_index = len(series) - 1
            normalised = _normalise_value(condition.value)
            fired, observed = _evaluate(
                series, condition.operator, normalised, anchor_index
            )
            if fired:
                fired_count += 1
                if observed is not None:
                    captured[f"{condition.indicator}.{col_name}"] = float(observed)

        if any_skipped and fired_count == 0:
            continue  # pragma: no cover - every condition skipped

        required = len(params.conditions) if params.combine == "and" else 1
        if fired_count >= required:
            as_of_for_row: date | str
            last_index = symbol_df.index.max()
            if hasattr(last_index, "date") and callable(last_index.date):
                as_of_for_row = (
                    last_index.date()
                )  # pragma: no cover - object index path used in practice
            elif isinstance(last_index, date):
                as_of_for_row = last_index
            else:  # pragma: no cover - unexpected index type
                as_of_for_row = str(last_index)
            matches.append(
                ScreenMatch(
                    symbol=str(symbol),
                    as_of_date=as_of_for_row,
                    matched_conditions=fired_count,
                    values=captured,
                )
            )
    return OBBject(results=matches)


__all__ = [
    "Operator",
    "ScreenCondition",
    "ScreenMatch",
    "ScreenQueryParams",
    "screen",
    "router",
]
