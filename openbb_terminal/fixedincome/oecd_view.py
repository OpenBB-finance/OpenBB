""" OECD view """
__docformat__ = "numpy"

from typing import Optional, List
import logging
import os
import pandas as pd

from matplotlib import pyplot as plt

from openbb_terminal.config_terminal import theme
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    is_valid_axes_count,
)
from openbb_terminal.fixedincome import oecd_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def plot_short_term_interest_rate(
    countries: list = None,
    forecast: bool = False,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    sheet_name: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Gets long term interest rates data from selected countries.

    Short-term interest rates are the rates at which short-term borrowings are effected between financial
    institutions or the rate at which short-term government paper is issued or traded in the market. Short-term
    interest rates are generally averages of daily rates, measured as a percentage. Short-term interest rates are
    based on three-month money market rates where available. Typical standardised names are "money market rate" and
    "treasury bill rate".

    Parameters
    ----------
    countries: list
        List of countries to get data for
    forecast: bool
        If True, plot forecasts for short term interest rates
    start_date: str
        Start date of data, in YYYY-MM-DD format
    end_date: str
        End date of data, in YYYY-MM-DD format
    export: str
        Export data to csv or excel file
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list)
    """
    df = oecd_model.get_interest_rate_data(
        f"short{'_forecast' if forecast else ''}",
        countries,
        start_date if start_date is not None else "",
        end_date if end_date is not None else "",
    )

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    ax.plot(
        df.index,
        df.values,
        marker="o",
        linestyle="dashed",
        linewidth=2,
        markersize=4,
    )
    ax.set_title(
        f"Short term interest rates{' forecasts' if forecast else ''} [Percent]"
    )
    ax.legend(countries)
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"stir",
        pd.DataFrame(df, columns=["STIR"]) / 100,
        sheet_name
    )


@log_start_end(log=logger)
def plot_long_term_interest_rate(
    countries: list = None,
    forecast: bool = False,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    sheet_name: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Gets long term interest rates data from selected countries.

    Long-term interest rates refer to government bonds maturing in ten years. Rates are mainly determined by the
    price charged by the lender, the risk from the borrower and the fall in the capital value. Long-term interest
    rates are generally averages of daily rates, measured as a percentage. These interest rates are implied by the
    prices at which the government bonds are traded on financial markets, not the interest rates at which the loans
    were issued. In all cases, they refer to bonds whose capital repayment is guaranteed by governments. Long-term
    interest rates are one of the determinants of business investment. Low long-term interest rates encourage
    investment in new equipment and high interest rates discourage it. Investment is, in turn, a major source of
    economic growth.

    Parameters
    ----------
    countries: list
        List of countries to get data for
    forecast: bool
        If True, plot forecasts for long term interest rates
    start_date: str
        Start date of data, in YYYY-MM-DD format
    end_date: str
        End date of data, in YYYY-MM-DD format
    export: str
        Export data to csv or excel file
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list)
    """
    df = oecd_model.get_interest_rate_data(
        f"long{'_forecast' if forecast else ''}",
        countries,
        start_date if start_date is not None else "",
        end_date if end_date is not None else "",
    )

    # This plot has 1 axis
    if not external_axes:
        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    ax.plot(
        df.index,
        df.values,
        marker="o",
        linestyle="dashed",
        linewidth=2,
        markersize=4,
    )
    ax.set_title(
        f"Long term interest rates{' forecasts' if forecast else ''} [Percent]"
    )
    ax.legend(countries)
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"ltir",
        pd.DataFrame(df, columns=["LTIR"]) / 100,
        sheet_name
    )
