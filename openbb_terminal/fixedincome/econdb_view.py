""" EconDB view """
__docformat__ = "numpy"

import logging
import os
from typing import Optional

import pandas as pd

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.fixedincome import econdb_model
from openbb_terminal.helper_funcs import export_data

logger = logging.getLogger(__name__)

MATURITY_TO_ID = {
    "4_week": "4w",
    "3_month": "3m",
    "6_month": "6m",
    "1_year": "1y",
    "1_month": "1m",
    "2_year": "2y",
    "3_year": "3y",
    "5_year": "5y",
    "7_year": "7y",
    "10_year": "10y",
    "20_year": "20y",
    "30_year": "30y",
}


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_cmn(
    maturity: str = "3_month",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: bool = False,
):
    """Plot Treasury Constant Maturity Nominal Market Yield.

    Yields on Treasury nominal securities at “constant maturity” are interpolated by the U.S. Treasury from the daily
    yield curve for non-inflation-indexed Treasury securities. This curve, which relates the yield on a security to
    its time to maturity, is based on the closing market bid yields on actively traded Treasury securities in the
    over-the-counter market. These market yields are calculated from composites of quotations obtained by the Federal
    Reserve Bank of New York. The constant maturity yield values are read from the yield curve at fixed maturities,
    currently 1, 3, and 6 months and 1, 2, 3, 5, 7, 10, 20, and 30 years. This method provides a yield for a 10-year
    maturity, for example, even if no outstanding security has exactly 10 years remaining to maturity. Similarly,
    yields on inflation-indexed securities at “constant maturity” are interpolated from the daily yield curve for
    Treasury inflation protected securities in the over-the-counter market. The inflation-indexed constant maturity
    yields are read from this yield curve at fixed maturities, currently 5, 7, 10, 20, and 30 years.

    Parameters
    ----------
    maturity: str
        Maturity to plot, options: ['1_month', '3_month', '6_month', '1_year', '2_year',
        '3_year', '5_year', '7_year', '10_year', '20_year', '30_year']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df = econdb_model.get_treasuries(
        instruments=["nominal"],
        maturities=[MATURITY_TO_ID[maturity]],
        frequency="daily",
        start_date=start_date,
        end_date=end_date,
    )

    fig = OpenBBFigure()
    fig.set_title(
        f"{maturity.replace('-', ' ')} Treasury Constant Maturity Nominal Market Yield [Percent]"
    )

    fig.add_scatter(
        x=df.index, y=df.values, name=maturity.replace("_", " "), mode="lines"
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"cmn, {maturity}",
        pd.DataFrame(df, columns=[maturity]) / 100,
        figure=fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_tips(
    maturity: str = "10_year",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: bool = False,
):
    """Plot Yields on Treasury inflation protected securities (TIPS) adjusted to constant maturities.

    Yields on Treasury nominal securities at “constant maturity” are interpolated by the U.S. Treasury from the daily
    yield curve for non-inflation-indexed Treasury securities. This curve, which relates the yield on a security to
    its time to maturity, is based on the closing market bid yields on actively traded Treasury securities in the
    over-the-counter market. These market yields are calculated from composites of quotations obtained by the Federal
    Reserve Bank of New York. The constant maturity yield values are read from the yield curve at fixed maturities,
    currently 1, 3, and 6 months and 1, 2, 3, 5, 7, 10, 20, and 30 years. This method provides a yield for a 10-year
    maturity, for example, even if no outstanding security has exactly 10 years remaining to maturity. Similarly,
    yields on inflation-indexed securities at “constant maturity” are interpolated from the daily yield curve for
    Treasury inflation protected securities in the over-the-counter market. The inflation-indexed constant maturity
    yields are read from this yield curve at fixed maturities, currently 5, 7, 10, 20, and 30 years.

    Parameters
    ----------
    maturity: str
        Maturity to plot, options: ['5_year', '7_year', '10_year', '20_year', '30_year']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df = econdb_model.get_treasuries(
        instruments=["inflation"],
        maturities=[MATURITY_TO_ID[maturity]],
        frequency="daily",
        start_date=start_date,
        end_date=end_date,
    )

    fig = OpenBBFigure()
    fig.set_title(
        f"{maturity.replace('-', ' ')} Yields on Treasury inflation protected securities (TIPS) adjusted to "
        f"constant maturities [Percent]"
    )

    fig.add_scatter(
        x=df.index, y=df.values, name=maturity.replace("_", " "), mode="lines"
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"tips, {maturity}",
        pd.DataFrame(df, columns=[maturity]) / 100,
        figure=fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_tbill(
    maturity: str = "3_month",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: bool = False,
):
    """Plot the Treasury Bill Secondary Market Rate.

    A Treasury Bill (T-Bill) is a short-term U.S. government debt obligation backed by the Treasury Department with a
    maturity of one year or less. Treasury bills are usually sold in denominations of $1,000. However, some can reach
    a maximum denomination of $5 million in non-competitive bids. These securities are widely regarded as low-risk
    and secure investments.

    Parameters
    ----------
    maturity: str
        Maturity to plot, options: ['4_week', '3_month', '6_month', '1_year']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df = econdb_model.get_treasuries(
        instruments=["secondary"],
        maturities=[MATURITY_TO_ID[maturity]],
        frequency="daily",
        start_date=start_date,
        end_date=end_date,
    )

    fig = OpenBBFigure()
    fig.set_title(
        f"{maturity.replace('-', ' ')} Treasury Bill Secondary Market Rate, Discount Basis [Percent]"
    )

    fig.add_scatter(
        x=df.index, y=df.values, name=maturity.replace("_", " "), mode="lines"
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"tbill, {maturity}",
        pd.DataFrame(df, columns=[maturity]) / 100,
        figure=fig,
    )

    return fig.show(external=external_axes)
