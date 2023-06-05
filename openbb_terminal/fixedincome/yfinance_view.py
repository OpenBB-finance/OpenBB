""" Yahoo Finance view """
__docformat__ = "numpy"

import logging
import os
from typing import Optional

import pandas as pd

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.fixedincome import yfinance_model
from openbb_terminal.helper_funcs import export_data

logger = logging.getLogger(__name__)

TY_TO_ID = {
    "5_year": "^FVX",
    "10_year": "^TNX",
    "30_year": "^TYX",
}


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_ty(
    maturity: str = "5_year",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: bool = False,
):
    """Plot Treasury Yield.

    Parameters
    ----------
    maturity: str
        Maturity to plot, options: ['5_year', '10_year', '30_year']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df = yfinance_model.get_series(
        TY_TO_ID[maturity], start_date=start_date, end_date=end_date
    )

    fig = OpenBBFigure()
    fig.set_title(f"{maturity.replace('-', ' ')} Treasury Yield [Percent]")

    fig.add_scatter(
        x=df.index, y=df.values, name=maturity.replace("_", " "), mode="lines"
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        maturity,
        pd.DataFrame(df, columns=[maturity]) / 100,
        figure=fig,
    )

    return fig.show(external=external_axes)
