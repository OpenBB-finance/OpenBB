"""Charting Extension Query Params."""

from typing import List, Optional, Union

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class FredSeriesChartQueryParams(QueryParams):
    """
    FRED Series Chart Query Params.

    kwargs
    ------

        data : List[Data], optional
            Filtered versions of the data contained in the original results.
            Example use is to reduce the number of columns or the length of data to plot.
            To supply additional columns, set `allow_unsafe = True`.
        title : str, optional
            Title of the chart.
        y1title : str, optional
            Right Y-axis title.
        y2title : str, optional
            Left Y-axis title.
        xtitle : str, optional
            X-axis title.
        dropnan: bool, optional (default: True)
            If True, rows containing NaN will be dropped.
        normalize: bool, optional (default: False)
            If True, the data will be normalized and placed on the same axis.
        allow_unsafe: bool, optional (default: False)
            If True, the method will attempt to pass all supplied data to the chart constructor.
            This can result in unexpected behavior.
    """

    data: Optional[Union[Data, List[Data]]] = Field(
        default=None,
        description="Filtered versions of the data contained in the original `self.results`."
        + " Columns should be the same as the original data."
        + " Example use is to reduce the number of columns or the length of data to plot."
        + " To supply additional columns, set `allow_unsafe = True`.",
    )
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


class TechnicalConesChartQueryParams(QueryParams):
    """
    Technical Cones Chart Query Params.

    kwargs
    ------

        data : List[Data], optional
            Filtered versions of the data contained in the original results.
            Example use is to reduce the number of windows to plot.
        title : str, optional
            Title of the chart.
        symbol: str, optional
            Symbol represented by the data. Used to label the chart.
    """

    data: Optional[Union[Data, List[Data]]] = Field(
        default=None,
        description="Filtered versions of the data contained in the original results."
        + " Columns should be the same as the original data."
        + " Example use is to reduce the number of columns or the length of data to plot.",
    )
    title: Optional[str] = Field(
        default=None,
        description="Title of the chart.",
    )
    symbol: Optional[str] = Field(
        default=None,
        description="Symbol represented by the data. Used to label the chart.",
    )
