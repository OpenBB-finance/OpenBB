from typing import Any, Dict, Optional, Tuple, Union

import pandas as pd
from openbb_charting.core.openbb_figure import OpenBBFigure
from openbb_charting.core.plotly_ta.data_classes import ChartIndicators
from openbb_charting.core.plotly_ta.ta_class import PlotlyTA
from openbb_core.app.model.charts.charting_settings import ChartingSettings


def to_chart(
    charting_settings: ChartingSettings,
    data: Union[pd.DataFrame, pd.Series],
    indicators: Optional[Union[ChartIndicators, Dict[str, Dict[str, Any]]]] = None,
    symbol: str = "",
    candles: bool = True,
    volume: bool = True,
    prepost: bool = False,
    volume_ticks_x: int = 7,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    """
    Returns the plotly json representation of the chart.
    This function is used so it can be called at the module level and used out of the box,
    which allows some more flexibility, ease of use and doesn't require the user to know
    about the PlotlyTA class.

    Parameters
    ----------
    charting_settings : ChartingSettings
        Charting settings.
    data : Union[pd.DataFrame, pd.Series]
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

    try:
        ta = PlotlyTA(charting_settings=charting_settings)
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
