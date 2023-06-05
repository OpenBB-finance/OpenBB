"""Volume View"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, Union

import pandas as pd

from openbb_terminal import OpenBBFigure
from openbb_terminal.common.technical_analysis import ta_helpers
from openbb_terminal.core.plots.plotly_ta.ta_class import PlotlyTA
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_ad(
    data: pd.DataFrame,
    use_open: bool = False,
    symbol: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots AD technical indicator

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of ohlc prices
    use_open : bool
        Whether to use open prices in calculation
    symbol : str
        Ticker symbol
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data as
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    ta = PlotlyTA()
    fig = ta.plot(data, dict(ad=dict(use_open=use_open)), f"{symbol.upper()} AD", False)

    if ta_helpers.check_columns(data) is None:
        return None

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "ad",
        ta.df_ta,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_adosc(
    data: pd.DataFrame,
    fast: int = 3,
    slow: int = 10,
    use_open: bool = False,
    symbol: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots AD Osc Indicator

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of ohlc prices
    use_open : bool
        Whether to use open prices in calculation
    fast: int
        Length of fast window
    slow : int
        Length of slow window
    symbol : str
        Stock ticker
    export : str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    ta = PlotlyTA()
    fig = ta.plot(
        data,
        dict(adosc=dict(fast=fast, slow=slow, use_open=use_open)),
        f"{symbol.upper()} AD Oscillator",
        False,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "adosc",
        ta.df_ta,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_obv(
    data: pd.DataFrame,
    symbol: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots OBV technical indicator

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of ohlc prices
    symbol : str
        Ticker
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data as
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    ta = PlotlyTA()
    fig = ta.plot(data, dict(obv=dict()), f"{symbol.upper()} OBV", False)

    close_col = ta_helpers.check_columns(data)
    if close_col is None:
        return None

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "obv",
        ta.df_ta,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)
