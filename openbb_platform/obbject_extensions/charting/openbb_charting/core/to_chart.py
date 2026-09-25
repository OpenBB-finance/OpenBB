"""Module containing the to_chart function."""

from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from openbb_charting.core.plotly_ta.data_classes import ChartIndicators  # noqa
    from openbb_charting.core.openbb_figure import OpenBBFigure  # noqa
    from pandas import DataFrame, Series  # noqa


def to_chart(
    data: Union["DataFrame", "Series"],
    indicators: Union["ChartIndicators", dict[str, dict[str, Any]]] | None = None,
    symbol: str = "",
    candles: bool = True,
    volume: bool = True,
    prepost: bool = False,
    volume_ticks_x: int = 7,
) -> tuple["OpenBBFigure", dict[str, Any]]:
    """Return the plotly json representation of the chart.

    Parameters
    ----------
    data : Union[DataFrame, Series]
        Data to be plotted.
    indicators : Optional[Union[ChartIndicators, Dict[str, Dict[str, Any]]]], optional
        Indicators to be plotted, by default None
    symbol : str, optional
        Symbol to be plotted, by default ""
    candles : bool, optional
        If True, candles will be plotted, by default True
    volume : bool, optional
        If True, volume will be plotted, by default True
    prepost : bool, optional
        If True, prepost will be plotted, by default False
    volume_ticks_x : int, optional
        Volume ticks, by default 7

    Returns
    -------
    Tuple[OpenBBFigure, Dict[str, Any]]
        Tuple containing the OpenBBFigure and the plotly json representation of the chart.
    """
    from openbb_charting.core.plotly_ta.ta_class import PlotlyTA

    try:
        ta = PlotlyTA()
        fig = ta.plot(
            df_stock=data,
            indicators=indicators,
            symbol=symbol,
            candles=candles,
            volume=volume,
            prepost=prepost,
            volume_ticks_x=volume_ticks_x,
        )
        content = fig.show(external=True).to_plotly_json()

        return fig, content
    except Exception as e:
        raise Exception(
            f"Failed to convert results to chart. Ensure the provided data is a valid time series. {e}"
        ) from e
