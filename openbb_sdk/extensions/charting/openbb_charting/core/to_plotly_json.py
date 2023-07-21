from typing import Union, Optional, Dict, Any

import pandas as pd
from openbb_charting.core.plotly_ta.ta_class import PlotlyTA
from openbb_charting.core.plotly_ta.data_classes import ChartIndicators
from openbb_core.app.model.charts.charting_settings import ChartingSettings


def to_plotly_json(
    charting_settings: ChartingSettings,
    data: Union[pd.DataFrame, pd.Series],
    indicators: Optional[Union[ChartIndicators, Dict[str, Dict[str, Any]]]] = None,
    symbol: str = "",
    candles: bool = True,
    volume: bool = True,
    prepost: bool = False,
    volume_ticks_x: int = 7,
) -> str:
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

    return fig.show(external=True).to_plotly_json()
