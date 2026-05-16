"""Multi-indicator composition endpoint."""

from collections.abc import Callable
from datetime import (
    date as dateType,
    datetime,
)
from importlib import import_module
from typing import Any

from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

# Bare 'date' alias for function signatures so the static-package builder
# writes 'date' (which it imports from datetime) rather than 'dateType' which it does not.
date = dateType


router = Router(prefix="", description="Compose multiple indicators on one series.")


_PREFERRED_MODULES: tuple[str, ...] = (
    "openbb_technical.indicators.overlays",
    "openbb_technical.indicators.oscillators",
    "openbb_technical.indicators.volatility",
    "openbb_technical.indicators.volume",
    "openbb_technical.indicators.trend",
    "openbb_technical.indicators.structure",
    "openbb_technical.indicators.statistics",
    "openbb_technical.signals.breakouts",
    "openbb_technical.signals.crossovers",
    "openbb_technical.signals.divergences",
    "openbb_technical.signals.patterns",
    "openbb_technical.signals.regime",
    "openbb_technical.signals.thresholds",
    "openbb_technical.technical_router",
)


def _resolve_indicator(name: str) -> Callable[..., Any] | None:
    """Look up an indicator endpoint by name across the known modules."""
    for module_path in _PREFERRED_MODULES:
        try:
            module = import_module(module_path)
        except ImportError:  # pragma: no cover - sibling family absent
            continue
        fn = getattr(module, name, None)
        if callable(fn):
            return fn
    return None  # pragma: no cover - guarded at the caller


def _call_indicator(fn: Callable[..., Any], **kwargs: Any) -> Any:
    """Invoke an indicator endpoint, building its QueryParams model from kwargs.

    Every router endpoint takes a single ``params: XxxQueryParams`` argument.
    The model class is read from the function signature and instantiated from
    ``kwargs``; any kwarg the model does not declare (e.g. ``target`` for an
    endpoint with no target field) is dropped so construction does not fail.
    """
    import inspect

    qp_class = next(iter(inspect.signature(fn).parameters.values())).annotation
    accepted = {k: v for k, v in kwargs.items() if k in qp_class.model_fields}
    return fn(qp_class(**accepted))


class MultiIndicatorRequest(QueryParams):
    """Describe one indicator the caller wants computed.

    Parameters
    ----------
    indicator : str
        Indicator endpoint name. Must match a registered router endpoint, e.g.
        ``rsi`` or ``bbands``.
    params : dict[str, float | int | str], optional
        Keyword arguments forwarded to the indicator endpoint. Empty by default.
    """

    indicator: str = Field(
        description="Indicator name. Must match a registered router endpoint, e.g. ``rsi`` or ``bbands``.",
    )
    params: dict[str, float | int | str] = Field(
        default_factory=dict,
        description="Keyword arguments forwarded to the indicator endpoint.",
    )


class MultiQueryParams(QueryParams):
    """Query parameters for the multi-indicator composition endpoint.

    Parameters
    ----------
    data : list[Data]
        Input OHLC(V) price series, shared by every requested indicator.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    indicators : list[MultiIndicatorRequest]
        Indicators to compute, in arbitrary order. Each entry pairs an
        endpoint name with its keyword arguments.
    target : str, optional
        Target column forwarded to indicators that accept one, by default
        ``"close"``.
    """

    __category__ = "multi"
    __output_columns__ = ("date", "values")

    data: list[Data] = Field(description="Input OHLC(V) series.")
    index: str = Field(default="date", description="Index column name in ``data``.")
    indicators: list[MultiIndicatorRequest] = Field(
        description="Indicators to compute, in arbitrary order.",
    )
    target: str = Field(
        default="close",
        description="Target column forwarded to indicators that accept one.",
    )


class MultiResultRow(Data):
    """One merged row across every requested indicator.

    Parameters
    ----------
    date : date | str
        Observation date for the merged row.
    values : dict[str, float | None]
        Indicator outputs for this date, keyed as ``"<indicator>.<column>"``.
        Only numeric columns are retained; non-numeric outputs are skipped.
        ``None`` values mark warm-up rows where the indicator has not yet
        produced a finite reading.
    """

    date: datetime | dateType | str = Field(description="Observation date.")
    values: dict[str, float | None] = Field(
        description=(
            "Indicator outputs for this date keyed as "
            '``"<indicator>.<column>"``. Numeric columns only — non-'
            "numeric outputs are skipped."
        ),
    )


def _to_records(obbject: Any) -> list[dict[str, Any]]:
    """Coerce an OBBject's ``results`` into a list of plain dicts."""
    results = getattr(obbject, "results", obbject)
    if results is None:  # pragma: no cover - defensive
        return []
    out: list[dict[str, Any]] = []
    for row in results:
        if hasattr(row, "model_dump"):
            out.append(row.model_dump())
        elif isinstance(row, dict):
            out.append(row)
        else:  # pragma: no cover - unexpected row shape
            out.append(dict(row))
    return out


def _row_key(row: dict[str, Any], index: str) -> Any:
    """Best-effort extraction of the date key for merging."""
    if index in row:
        return row[index]
    if "date" in row:  # pragma: no cover - alias kept for safety
        return row["date"]
    return None  # pragma: no cover - endpoint without a date column


_SENTINEL_COLUMNS = {"date", "open", "high", "low", "close", "volume", "adj_close"}


def _numeric_columns(row: dict[str, Any], target: str) -> dict[str, float | None]:
    """Keep only numeric columns that aren't part of the input OHLCV bar."""
    out: dict[str, float | None] = {}
    sentinels = _SENTINEL_COLUMNS | {target}
    for key, value in row.items():
        if key in sentinels:
            continue
        if value is None:
            out[key] = None
            continue
        if isinstance(value, bool):
            continue  # pragma: no cover - indicators don't emit bools today
        if isinstance(value, (int, float)):
            out[key] = float(value)
    return out


@router.command(methods=["POST"])
def multi(params: MultiQueryParams) -> OBBject[list[MultiResultRow]]:
    """Run multiple indicators on a single price series and merge them by date."""

    merged: dict[Any, dict[str, float | None]] = {}

    for request in params.indicators:
        fn = _resolve_indicator(request.indicator)
        if fn is None:
            continue
        result = _call_indicator(
            fn,
            data=params.data,
            index=params.index,
            target=params.target,
            **request.params,
        )
        rows = _to_records(result)
        for row in rows:
            key = _row_key(row, params.index)
            if key is None:  # pragma: no cover - defensive
                continue
            numeric = _numeric_columns(row, params.target)
            bucket = merged.setdefault(key, {})
            for col, value in numeric.items():
                bucket[f"{request.indicator}.{col}"] = value

    ordered_keys = sorted(merged.keys(), key=str)
    out_rows = [
        MultiResultRow(date=key, values=merged[key])  # ty: ignore[invalid-argument-type]
        for key in ordered_keys
    ]
    return OBBject(results=out_rows)


__all__ = [
    "MultiIndicatorRequest",
    "MultiQueryParams",
    "MultiResultRow",
    "multi",
    "router",
]
