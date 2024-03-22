"""Charting Extension Query Params."""

from typing import Any, Dict, List, Optional, Union

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

from openbb_charting.core.to_chart import ChartIndicators


def _get_type_name(t):
    """Get the type name of a type hint."""
    if hasattr(t, "__origin__"):
        return f"{t.__origin__.__name__}[{', '.join([_get_type_name(arg) for arg in t.__args__])}]"
    return t.__name__


class ChartQueryParams(QueryParams):
    """Chart Query Parmams Base Model."""

    def __init__(self, **data):
        super().__init__(**data)
        self.__doc__ = self.__repr__()

    def __repr__(self):
        fields = self.__class__.model_fields
        repr_str = (
            "\n"
            + self.__class__.__name__
            + "\n\n"
            + "    Parameters\n"
            + "    ----------\n"
            + "\n".join(
                [
                    f"\n    {k} ({_get_type_name(v.annotation)}):\n        {v.description}".replace(
                        ". ", ".\n        "
                    )
                    for k, v in fields.items()
                ]
            )
        )
        return repr_str

    data: Optional[Union[Data, List[Data]]] = Field(
        default=None,
        description="Filtered versions of the data contained in the original `self.results`."
        + " Columns should be the same as the original data."
        + " Example use is to reduce the number of columns, or the length of data, to plot.",
    )


class EquityPriceHistoricalChartQueryParams(ChartQueryParams):
    """Historical Price Chart Query Params."""

    title: Optional[str] = Field(
        default=None,
        description="Title of the chart.",
    )
    target_column: Optional[str] = Field(
        default=None,
        description="The specific column to target. If supplied, this will override the candles and volume parameters.",
    )
    multi_symbol: bool = Field(
        default=False,
        description="Flag to indicate whether the data contains multiple symbols."
        + " This is mostly handled automatically, but if the chart fails to generate try setting this to True.",
    )
    same_axis: bool = Field(
        default=False,
        description="If True, forces all data to be plotted on the same axis.",
    )
    normalize: bool = Field(
        default=False,
        description="If True, the data will be normalized and placed on the same axis.",
    )
    returns: bool = Field(
        default=False,
        description="If True, the cumulative returns for the length of the time series will be calculated and plotted.",
    )
    candles: bool = Field(
        default=True,
        description="If True, and OHLC exists, and there is only one symbol in the data, candles will be plotted.",
    )
    heikin_ashi: bool = Field(
        default=False,
        description="If True, and `candles=True`, Heikin Ashi candles will be plotted.",
    )
    volume: bool = Field(
        default=True,
        description="If True, and volume exists, and `candles=True`, volume will be plotted.",
    )
    indicators: Optional[Union[ChartIndicators, Dict[str, Dict[str, Any]]]] = Field(
        default=None,
        description="Indicators to be plotted, formatted as a dictionary."
        + " Data containing multiple symbols will ignore indicators."
        + """
        Example:
            indicators = dict(
                sma=dict(length=[20,30,50]),
                adx=dict(length=14),
                rsi=dict(length=14),
            )""",
    )


class EconomyFredSeriesChartQueryParams(ChartQueryParams):
    """FRED Series Chart Query Params."""

    title: Optional[str] = Field(
        default=None,
        description="Title of the chart.",
    )
    y1title: Optional[str] = Field(
        default=None,
        description="Right Y-axis title.",
    )
    y2title: Optional[str] = Field(
        default=None,
        description="Left Y-axis title.",
    )
    xtitle: Optional[str] = Field(
        default=None,
        description="X-axis title.",
    )
    dropnan: bool = Field(
        default=True,
        description="If True, rows containing NaN will be dropped.",
    )
    normalize: bool = Field(
        default=False,
        description="If True, the data will be normalized and placed on the same axis.",
    )
    allow_unsafe: bool = Field(
        default=False,
        description="If True, the method will attempt to pass all supplied data to the chart constructor."
        + " This can result in unexpected behavior.",
    )


class TechnicalConesChartQueryParams(ChartQueryParams):
    """Technical Cones Chart Query Params."""

    title: Optional[str] = Field(
        default=None,
        description="Title of the chart.",
    )
    symbol: Optional[str] = Field(
        default=None,
        description="Symbol represented by the data. Used to label the chart.",
    )


class ChartParams:
    """Chart Query Params."""

    equity_price_historical = EquityPriceHistoricalChartQueryParams
    economy_fred_series = EconomyFredSeriesChartQueryParams
    equity_price_historical = EquityPriceHistoricalChartQueryParams
    etf_historical = EquityPriceHistoricalChartQueryParams
    index_price_historical = EquityPriceHistoricalChartQueryParams
    technical_cones = TechnicalConesChartQueryParams
