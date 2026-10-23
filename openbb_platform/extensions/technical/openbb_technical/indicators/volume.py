"""Volume-family technical indicators."""

from datetime import (
    date as dateType,
    datetime,
)

from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.app.utils import basemodel_to_df
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, PositiveInt

from openbb_technical.helpers import validate_data

# Bare 'date' alias for function signatures so the static-package builder
# writes 'date' (which it imports from datetime) rather than 'dateType' which it does not.
date = dateType


router = Router(prefix="", description="Volume indicators.")


class ObvQueryParams(QueryParams):
    """Query parameters for the On-Balance Volume endpoint.

    Parameters
    ----------
    data : list[Data]
        OHLCV price series. ``close`` and ``volume`` columns are required.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    offset : int, optional
        Shift the output series by this many bars, by default 0.
    """

    __category__ = "volume"
    __output_columns__ = ("date", "obv")

    data: list[Data] = Field(description="Input OHLCV price series.")
    index: str = Field(default="date", description="Index column name in ``data``.")
    offset: int = Field(default=0, description="Periods to offset the result.")


class ObvData(Data):
    """One row of the On-Balance Volume time series.

    Parameters
    ----------
    date : date | str
        Observation date.
    obv : float, optional
        On-Balance Volume cumulative total at this bar.
    """

    date: datetime | dateType | str = Field(description="Observation date.")
    obv: float | None = Field(description="On-Balance Volume cumulative total.")


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="OBV on daily TSLA.",
            code=[
                "data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').results",
                "obv = obb.technical.obv(data=data)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries")}),
    ],
)
def obv(params: ObvQueryParams) -> OBBject[list[ObvData]]:
    """Calculate On-Balance Volume (OBV), a cumulative volume-flow indicator."""
    import pandas as pd
    import pandas_ta as ta  # noqa: F401

    df = basemodel_to_df(params.data, index=params.index)
    series = df.ta.obv(offset=params.offset)
    out = (
        pd.DataFrame({"obv": series})
        .dropna()
        .reset_index()
        .rename(columns={params.index: "date"})
    )
    return OBBject(results=[ObvData(**row) for row in out.to_dict(orient="records")])


class AdQueryParams(QueryParams):
    """Query parameters for the Accumulation/Distribution line endpoint.

    Parameters
    ----------
    data : list[Data]
        OHLCV price series. ``high``, ``low``, ``close``, and ``volume`` are
        required.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    offset : int, optional
        Shift the output series by this many bars, by default 0.
    """

    __category__ = "volume"
    __output_columns__ = ("date", "ad")

    data: list[Data] = Field(description="Input OHLCV price series.")
    index: str = Field(
        default="date",
        description='Index column name in ``data``, by default ``"date"``.',
    )
    offset: int = Field(default=0, description="Periods to offset the result.")


class AdData(Data):
    """One row of the Accumulation/Distribution line time series.

    Parameters
    ----------
    date : date | str
        Observation date.
    ad : float, optional
        Accumulation/Distribution cumulative line value at this bar.
    """

    date: datetime | dateType | str = Field(description="Observation date.")
    ad: float | None = Field(description="Accumulation/Distribution cumulative line.")


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Accumulation/Distribution line on daily TSLA.",
            code=[
                "data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').results",
                "ad = obb.technical.ad(data=data)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries")}),
    ],
)
def ad(params: AdQueryParams) -> OBBject[list[AdData]]:
    """Calculate the Accumulation/Distribution line, a volume-flow indicator."""
    import pandas as pd
    import pandas_ta as ta  # noqa: F401

    df = basemodel_to_df(params.data, index=params.index)
    series = df.ta.ad(offset=params.offset)
    out = (
        pd.DataFrame({"ad": series})
        .dropna()
        .reset_index()
        .rename(columns={params.index: "date"})
    )
    return OBBject(results=[AdData(**row) for row in out.to_dict(orient="records")])


class AdoscQueryParams(QueryParams):
    """Query parameters for the Chaikin Accumulation/Distribution Oscillator endpoint.

    Parameters
    ----------
    data : list[Data]
        OHLCV price series. ``high``, ``low``, ``close``, and ``volume`` are
        required.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    fast : PositiveInt, optional
        Fast EMA window applied to the Accumulation/Distribution line, by
        default 3.
    slow : PositiveInt, optional
        Slow EMA window applied to the Accumulation/Distribution line, by
        default 10.
    offset : int, optional
        Shift the output series by this many bars, by default 0.
    """

    __category__ = "volume"
    __output_columns__ = ("date", "adosc")

    data: list[Data] = Field(description="Input OHLCV price series.")
    index: str = Field(
        default="date",
        description='Index column name in ``data``, by default ``"date"``.',
    )
    fast: PositiveInt = Field(default=3, description="Fast EMA window.")
    slow: PositiveInt = Field(default=10, description="Slow EMA window.")
    offset: int = Field(default=0, description="Periods to offset the result.")


class AdoscData(Data):
    """One row of the Chaikin Oscillator time series.

    Parameters
    ----------
    date : date | str
        Observation date.
    adosc : float, optional
        Chaikin Accumulation/Distribution Oscillator value at this bar.
    """

    date: datetime | dateType | str = Field(description="Observation date.")
    adosc: float | None = Field(
        description="Chaikin Accumulation/Distribution Oscillator."
    )


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Chaikin Oscillator on daily TSLA.",
            code=[
                "data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').results",
                "adosc = obb.technical.adosc(data=data, fast=3, slow=10)",
            ],
        ),
        APIEx(parameters={"fast": 2, "slow": 4, "data": APIEx.mock_data("timeseries")}),
    ],
)
def adosc(params: AdoscQueryParams) -> OBBject[list[AdoscData]]:
    """Calculate the Chaikin Accumulation/Distribution Oscillator."""
    import pandas as pd
    import pandas_ta as ta  # noqa: F401

    validate_data(params.data, [params.fast, params.slow])
    df = basemodel_to_df(params.data, index=params.index)
    series = df.ta.adosc(fast=params.fast, slow=params.slow, offset=params.offset)
    out = (
        pd.DataFrame({"adosc": series})
        .dropna()
        .reset_index()
        .rename(columns={params.index: "date"})
    )
    return OBBject(results=[AdoscData(**row) for row in out.to_dict(orient="records")])


class VwapQueryParams(QueryParams):
    """Query parameters for the Volume-Weighted Average Price endpoint.

    Parameters
    ----------
    data : list[Data]
        OHLCV price series. ``high``, ``low``, ``close``, and ``volume`` are
        required, and the index must be parseable as a datetime so that the
        resample anchor can be applied.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    anchor : str, optional
        Resample anchor — pandas offset alias such as ``"D"`` (daily),
        ``"W"`` (weekly), or ``"ME"`` (month-end). Determines the boundary at
        which the VWAP accumulator resets, by default ``"D"``.
    offset : int, optional
        Shift the output series by this many bars, by default 0.
    """

    __category__ = "volume"
    __output_columns__ = ("date", "vwap")

    data: list[Data] = Field(description="Input OHLCV price series.")
    index: str = Field(
        default="date",
        description='Index column name in ``data``, by default ``"date"``.',
    )
    anchor: str = Field(
        default="D",
        description=(
            "Resample anchor — pandas offset alias such as ``D``, ``W``, ``ME``. "
            "Determines the VWAP reset boundary."
        ),
    )
    offset: int = Field(default=0, description="Periods to offset the result.")


class VwapData(Data):
    """One row of the Volume-Weighted Average Price time series.

    Parameters
    ----------
    date : date | str
        Observation date.
    vwap : float, optional
        Volume-weighted average price at this bar, accumulated since the most
        recent anchor boundary.
    """

    date: datetime | dateType | str = Field(description="Observation date.")
    vwap: float | None = Field(description="Volume-weighted average price.")


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Daily-anchored VWAP on intraday TSLA.",
            code=[
                "data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').results",
                "vwap = obb.technical.vwap(data=data, anchor='D')",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries")}),
    ],
)
def vwap(params: VwapQueryParams) -> OBBject[list[VwapData]]:
    """Calculate the Volume-Weighted Average Price (VWAP), anchored at a chosen boundary."""
    import pandas as pd
    import pandas_ta as ta  # noqa: F401

    df = basemodel_to_df(params.data, index=params.index)
    if params.index == "date":
        df.index = pd.to_datetime(df.index)
    series = df.ta.vwap(anchor=params.anchor, offset=params.offset)
    out = (
        pd.DataFrame({"vwap": series})
        .dropna()
        .reset_index()
        .rename(columns={params.index: "date"})
    )
    return OBBject(results=[VwapData(**row) for row in out.to_dict(orient="records")])


__all__ = [
    "AdData",
    "AdQueryParams",
    "AdoscData",
    "AdoscQueryParams",
    "ObvData",
    "ObvQueryParams",
    "VwapData",
    "VwapQueryParams",
    "ad",
    "adosc",
    "obv",
    "router",
    "vwap",
]
