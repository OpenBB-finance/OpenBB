"""Pairwise rolling correlation and snapshot correlation matrix."""

from datetime import (
    date as dateType,
    datetime,
)
from itertools import combinations
from typing import Literal

from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.app.utils import basemodel_to_df
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, PositiveInt

# Bare 'date' alias for function signatures so the static-package builder
# writes 'date' (which it imports from datetime) rather than 'dateType' which it does not.
date = dateType


router = Router(prefix="", description="Cross-asset correlation endpoints.")


class CorrelationQueryParams(QueryParams):
    """Query parameters for the rolling pairwise correlation endpoint.

    Parameters
    ----------
    data : list[Data]
        Long-format multi-symbol price data. Must contain a ``symbol`` column
        and the chosen ``target`` price column.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    target : str, optional
        Column to compute correlation on, by default ``"close"``. Pairwise
        returns are derived from ``pct_change`` on this column.
    window : PositiveInt, optional
        Rolling window length in bars, by default 60.
    method : {"pearson", "spearman", "kendall"}, optional
        Correlation method passed through to ``pandas.DataFrame.corr``,
        by default ``"pearson"``.
    pairs : list[tuple[str, str]], optional
        Explicit list of ``(symbol_a, symbol_b)`` pairs. ``None`` (the
        default) enumerates every unique pair from the input symbols.
    """

    __category__ = "multi"
    __output_columns__ = ("date", "symbol_a", "symbol_b", "correlation")

    data: list[Data] = Field(
        description="Long-format multi-symbol price data with a ``symbol`` column.",
    )
    index: str = Field(default="date", description="Index column name in ``data``.")
    target: str = Field(
        default="close",
        description="Column to compute correlation on.",
    )
    window: PositiveInt = Field(
        default=60,
        description="Rolling window length in bars.",
    )
    method: Literal["pearson", "spearman", "kendall"] = Field(
        default="pearson",
        description="Correlation method passed through to ``pandas.DataFrame.corr``.",
    )
    pairs: list[tuple[str, str]] | None = Field(
        default=None,
        description=(
            "Optional explicit list of ``(symbol_a, symbol_b)`` pairs. "
            "Defaults to all unique pairs."
        ),
    )


class CorrelationData(Data):
    """One row of the rolling-correlation time series.

    Parameters
    ----------
    date : date | str
        Observation date.
    symbol_a : str
        First symbol of the pair.
    symbol_b : str
        Second symbol of the pair.
    correlation : float, optional
        Rolling correlation between ``symbol_a`` and ``symbol_b`` over the
        trailing ``window`` bars. ``None`` for warm-up rows where the window
        has not yet filled or where either series has a missing return.
    """

    date: datetime | dateType | str = Field(description="Observation date.")
    symbol_a: str = Field(description="First symbol of the pair.")
    symbol_b: str = Field(description="Second symbol of the pair.")
    correlation: float | None = Field(
        description="Rolling correlation between ``symbol_a`` and ``symbol_b``.",
    )


@router.command(methods=["POST"])
def correlation(params: CorrelationQueryParams) -> OBBject[list[CorrelationData]]:
    """Compute rolling pairwise correlation of returns across symbols."""
    import math

    df = basemodel_to_df(params.data, index=params.index)
    if "symbol" not in df.columns:
        raise ValueError("Input data must contain a 'symbol' column.")
    wide = df.pivot_table(
        index=df.index,
        columns="symbol",
        values=params.target,
        aggfunc="last",
    ).sort_index()
    returns = wide.pct_change()

    available = list(wide.columns)
    if params.pairs is None:
        pair_list = list(combinations(available, 2))
    else:
        pair_list = [
            (a, b) for (a, b) in params.pairs if a in available and b in available
        ]

    import pandas as pd

    rows: list[CorrelationData] = []
    for symbol_a, symbol_b in pair_list:
        sa = returns[symbol_a]
        sb = returns[symbol_b]
        if params.method == "pearson":
            series = sa.rolling(window=params.window).corr(sb)
        else:
            values: list[float] = []
            arr_a = sa.to_numpy()
            arr_b = sb.to_numpy()
            n = len(arr_a)
            for end in range(n):
                start = end - params.window + 1
                if start < 0:
                    values.append(float("nan"))
                    continue
                window_a = pd.Series(arr_a[start : end + 1])
                window_b = pd.Series(arr_b[start : end + 1])
                if window_a.isna().any() or window_b.isna().any():
                    values.append(float("nan"))
                    continue
                values.append(float(window_a.corr(window_b, method=params.method)))
            series = pd.Series(values, index=returns.index, dtype=float)
        for date_value, corr_value in series.items():
            value: float | None
            if corr_value is None or (
                isinstance(corr_value, float) and math.isnan(corr_value)
            ):
                value = None
            else:
                value = float(corr_value)
            rows.append(
                CorrelationData(
                    date=date_value,  # ty: ignore[invalid-argument-type]
                    symbol_a=symbol_a,
                    symbol_b=symbol_b,
                    correlation=value,
                )
            )
    return OBBject(results=rows)


class CorrelationMatrixQueryParams(QueryParams):
    """Query parameters for the snapshot correlation-matrix endpoint.

    Parameters
    ----------
    data : list[Data]
        Long-format multi-symbol price data. Must contain a ``symbol`` column
        and the chosen ``target`` price column.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    target : str, optional
        Column to correlate, by default ``"close"``.
    window : PositiveInt, optional
        If set, restrict the correlation calculation to the trailing
        ``window`` rows preceding ``as_of_date``. ``None`` (the default) uses
        every available row up to and including the anchor.
    method : {"pearson", "spearman", "kendall"}, optional
        Correlation method, by default ``"pearson"``.
    as_of_date : date | str, optional
        Anchor date for the snapshot. ``None`` (the default) uses the most
        recent row in the input.
    """

    __category__ = "multi"
    __output_columns__ = ("as_of_date", "symbols", "matrix")

    data: list[Data] = Field(
        description="Long-format multi-symbol price data with a ``symbol`` column.",
    )
    index: str = Field(default="date", description="Index column name in ``data``.")
    target: str = Field(default="close", description="Column to correlate.")
    window: PositiveInt | None = Field(
        default=None,
        description=(
            "If set, restrict correlation to the trailing ``window`` rows "
            "before ``as_of_date``. ``None`` uses every available row."
        ),
    )
    method: Literal["pearson", "spearman", "kendall"] = Field(
        default="pearson", description='Correlation method, by default ``"pearson"``.'
    )
    as_of_date: datetime | dateType | str | None = Field(
        default=None,
        description=(
            "Anchor date for the snapshot. ``None`` uses the last available "
            "row in the input."
        ),
    )


class CorrelationMatrixData(Data):
    """A square correlation matrix at a single point in time.

    Parameters
    ----------
    as_of_date : date | str
        Anchor date used to compute the snapshot.
    symbols : list[str]
        Symbols, in matrix order. ``matrix[i][j]`` is the correlation between
        ``symbols[i]`` and ``symbols[j]``.
    matrix : list[list[float]]
        Square correlation matrix, with diagonal elements equal to 1 and the
        matrix symmetric about the diagonal.
    """

    as_of_date: datetime | dateType | str = Field(
        description="Anchor date used for the snapshot."
    )
    symbols: list[str] = Field(description="Symbols, in matrix order.")
    matrix: list[list[float]] = Field(description="Correlation values.")


@router.command(methods=["POST"])
def correlation_matrix(
    params: CorrelationMatrixQueryParams,
) -> OBBject[list[CorrelationMatrixData]]:
    """Build a point-in-time correlation matrix across every symbol in the input."""
    import math

    import pandas as pd

    df = basemodel_to_df(params.data, index=params.index)
    if "symbol" not in df.columns:
        raise ValueError("Input data must contain a 'symbol' column.")
    wide = df.pivot_table(
        index=df.index,
        columns="symbol",
        values=params.target,
        aggfunc="last",
    ).sort_index()
    returns = wide.pct_change().dropna(how="all")

    if params.as_of_date is None:
        anchor = returns.index.max()
    else:
        anchor_ts = pd.to_datetime(params.as_of_date)
        anchor = anchor_ts.date() if hasattr(anchor_ts, "date") else anchor_ts

    sliced = returns.loc[[idx_val <= anchor for idx_val in returns.index]]
    if params.window is not None:
        sliced = sliced.tail(params.window)

    corr_df = sliced.corr(method=params.method)
    symbols = list(corr_df.columns)

    matrix: list[list[float]] = []
    for row_label in symbols:
        row: list[float] = []
        for col_label in symbols:
            value = corr_df.at[row_label, col_label]
            if value is None or (isinstance(value, float) and math.isnan(value)):
                row.append(float("nan"))  # pragma: no cover - all-aligned input
            else:
                row.append(float(value))
        matrix.append(row)

    as_of_out: datetime | dateType | str
    if hasattr(anchor, "date") and callable(
        anchor.date
    ):  # pragma: no cover - object-index path is used in practice
        as_of_out = anchor.date()  # ty: ignore[invalid-assignment, call-top-callable]
    elif isinstance(anchor, date):
        as_of_out = anchor
    else:  # pragma: no cover - unexpected anchor type
        as_of_out = str(anchor)

    return OBBject(
        results=[
            CorrelationMatrixData(
                as_of_date=as_of_out,
                symbols=symbols,
                matrix=matrix,
            )
        ]
    )


__all__ = [
    "CorrelationData",
    "CorrelationMatrixData",
    "CorrelationMatrixQueryParams",
    "CorrelationQueryParams",
    "correlation",
    "correlation_matrix",
    "router",
]
