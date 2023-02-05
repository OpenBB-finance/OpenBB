""" FRED view """
__docformat__ = "numpy"

from typing import Optional, List
from itertools import cycle
import logging
import os

import pandas as pd
from matplotlib import pyplot as plt

from openbb_terminal.config_terminal import theme
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import log_start_end, check_api_key
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    is_valid_axes_count,
    print_rich_table,
)
from openbb_terminal.fixedincome import fred_model
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

ID_TO_NAME_ESTR = {
    "ECBESTRVOLWGTTRMDMNRT": "Euro Short-Term Rate: Volume-Weighted Trimmed Mean Rate [Percent]",
    "ECBESTRTOTVOL": "Euro Short-Term Rate: Total Volume [Millions of EUR]",
    "ECBESTRNUMTRANS": "Euro Short-Term Rate: Number of Transactions",
    "ECBESTRRT75THPCTVOL": "Euro Short-Term Rate: Rate at 75th Percentile of Volume [Percent]",
    "ECBESTRNUMACTBANKS": "Euro Short-Term Rate: Number of Active Banks",
    "ECBESTRSHRVOL5LRGACTBNK": "Euro Short-Term Rate: Share of Volume of the 5 Largest Active Banks [Percent]",
    "ECBESTRRT25THPCTVOL": "Euro Short-Term Rate: Rate at 25th Percentile of Volume [Percent]",
}
ID_TO_NAME_SOFR = {
    "SOFR": "Secured Overnight Financing Rate (SOFR) [Percent]",
    "SOFR30DAYAVG": "30-Day Average SOFR [Percent]",
    "SOFR90DAYAVG": "90-Day Average SOFR [Percent]",
    "SOFR180DAYAVG": "180-Day Average SOFR [Percent]",
    "SOFRINDEX": "SOFR Index",
}
ID_TO_NAME_SONIA = {
    "IUDSOIA": "Daily Sterling Overnight Index Average (SONIA) Rate [Percent]",
    "IUDZOS2": "SONIA Compounded Index",
    "IUDZLS6": "SONIA Rate: 10th percentile [Percent]",
    "IUDZLS7": "SONIA Rate: 25th percentile [Percent]",
    "IUDZLS8": "SONIA Rate: 75th percentile [Percent]",
    "IUDZLS9": "SONIA Rate: 90th percentile [Percent]",
    "IUDZLT2": "SONIA Rate Total Nominal Value [Millions of GBP]",
}
ID_TO_NAME_AMERIBOR = {
    "AMERIBOR": "Overnight Unsecured AMERIBOR Benchmark Interest Rate [Percent]",
    "AMBOR30T": "AMERIBOR Term-30 Derived Interest Rate Index [Percent]",
    "AMBOR90T": "AMERIBOR Term-90 Derived Interest Rate Index [Percent]",
    "AMBOR1W": "1-Week AMERIBOR Term Structure of Interest Rates",
    "AMBOR1M": "1-Month AMERIBOR Term Structure of Interest Rates",
    "AMBOR3M": "3-Month AMERIBOR Term Structure of Interest Rates",
    "AMBOR6M": "6-Month AMERIBOR Term Structure of Interest Rates",
    "AMBOR1Y": "1-Year AMERIBOR Term Structure of Interest Rates",
    "AMBOR2Y": "2-Year AMERIBOR Term Structure of Interest Rates",
    "AMBOR30": "30-Day Moving Average AMERIBOR Benchmark Interest Rate",
    "AMBOR90": "90-Day Moving Average AMERIBOR Benchmark Interest Rate",
}
ID_TO_NAME_FFER = {
    "FEDFUNDS": "Monthly",
    "DFF": "Daily (incl. Weekends)",
    "FF": "Weekly",
    "RIFSPFFNB": "Daily (excl. Weekends)",
    "RIFSPFFNA": "Annual",
    "RIFSPFFNBWAW": "Biweekly",
}
ID_TO_NAME_EFFR = {
    "EFFR": "Effective Federal Funds Rate [Percent]",
    "EFFRVOL": "Effective Federal Funds Volume [Billions of USD]",
    "EFFR1": "Effective Federal Funds Rate: 1th Percentile [Percent]",
    "EFFR25": "Effective Federal Funds Rate: 25th Percentile [Percent]",
    "EFFR75": "Effective Federal Funds Rate: 75th Percentile [Percent]",
    "EFFR99": "Effective Federal Funds Rate: 99th Percentile [Percent]",
}
ID_TO_NAME_OBFR = {
    "OBFR": "Overnight Bank Funding Rate [Percent]",
    "OBFRVOL": "Overnight Bank Funding Volume [Billions of USD]",
    "OBFR1": "Overnight Bank Funding Rate: 1th Percentile [Percent]",
    "OBFR25": "Overnight Bank Funding Rate: 25th Percentile [Percent]",
    "OBFR75": "Overnight Bank Funding Rate: 75th Percentile [Percent]",
    "OBFR99": "Overnight Bank Funding Rate: 99th Percentile [Percent]",
}
ID_TO_NAME_DWPCR = {
    "MPCREDIT": "Monthly",
    "RIFSRPF02ND": "Daily (incl. Weekends)",
    "WPCREDIT": "Weekly",
    "DPCREDIT": "Daily (excl. Weekends)",
    "RIFSRPF02NA": "Annual",
}
ID_TO_NAME_TMC = {
    "T10Y3M": "3-Month",
    "T10Y2Y": "2-Year",
}
ID_TO_NAME_FFRMC = {
    "T10YFF": "10-Year",
    "T5YFF": "5-Year",
    "T1YFF": "1-Year",
    "T6MFF": "6-Month",
    "T3MFF": "3-Month",
}
ID_TO_NAME_SECONDARY = {
    "TB3MS": "3-Month",
    "DTB4WK": "4-Week",
    "DTB1YR": "1-Year",
    "DTB6": "6-Month"
}
ID_TO_NAME_TIPS = {
    "DFII5": "5-Year",
    "DFII7": "7-Year",
    "DFII10": "10-Year",
    "DFII20": "20-Year",
    "DFII30": "30-Year",
}
ID_TO_NAME_CMN = {
    "DGS1MO": "1 Month",
    "DGS3MO": "3 Month",
    "DGS6MO": "6 Month",
    "DGS1": "1 Year",
    "DGS2": "2 Year",
    "DGS3": "3 Year",
    "DGS5": "5 Year",
    "DGS7": "7 Year",
    "DGS10": "10 Year",
    "DGS20": "20 Year",
    "DGS30": "30 Year",
}
ID_TO_NAME_TBFFR = {
    "TB3SMFFM": "3 Month",
    "TB6SMFFM": "6 Month",
}


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_estr(
    series_id: str = "ECBESTRVOLWGTTRMDMNRT",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot Euro Short-Term Rate (ESTR)

    Parameters
    ----------
    series_id: str
        FRED ID of ESTR data to plot, options: ['ECBESTRVOLWGTTRMDMNRT', 'ECBESTRTOTVOL', 'ECBESTRNUMTRANS', 'ECBESTRRT75THPCTVOL', 'ECBESTRNUMACTBANKS', 'ECBESTRSHRVOL5LRGACTBNK', 'ECBESTRRT25THPCTVOL']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list)
    """
    df = fred_model.get_series_data(
        series_id=series_id, start_date=start_date, end_date=end_date
    )

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    colors = cycle(theme.get_colors())
    ax.plot(
        df.index,
        df.values,
        marker="o",
        linestyle="dashed",
        linewidth=2,
        markersize=4,
        color=next(colors, "#FCED00"),
    )
    ax.set_title(ID_TO_NAME_ESTR[series_id])
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"estr, {series_id}",
        df,
    )


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_sofr(
    series_id: str = "SOFR",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot Secured Overnight Financing Rate (SOFR)

    Parameters
    ----------
    series_id: str
        FRED ID of SOFR data to plot, options: ['SOFR', 'SOFR30DAYAVG', 'SOFR90DAYAVG', 'SOFR180DAYAVG', 'SOFRINDEX']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list)
    """
    df = fred_model.get_series_data(
        series_id=series_id, start_date=start_date, end_date=end_date
    )

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    colors = cycle(theme.get_colors())
    ax.plot(
        df.index,
        df.values,
        marker="o",
        linestyle="dashed",
        linewidth=2,
        markersize=4,
        color=next(colors, "#FCED00"),
    )
    ax.set_title(ID_TO_NAME_SOFR[series_id])
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"sofr, {series_id}",
        df,
    )


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_sonia(
    series_id: str = "IUDSOIA",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot Sterling Overnight Index Average (SONIA)

    Parameters
    ----------
    series_id: str
        FRED ID of SONIA data to plot, options: ['IUDSOIA', 'IUDZOS2', 'IUDZLS6', 'IUDZLS7', 'IUDZLS8', 'IUDZLS9', 'IUDZLT2']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list)
    """
    df = fred_model.get_series_data(
        series_id=series_id, start_date=start_date, end_date=end_date
    )

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    colors = cycle(theme.get_colors())
    ax.plot(
        df.index,
        df.values,
        marker="o",
        linestyle="dashed",
        linewidth=2,
        markersize=4,
        color=next(colors, "#FCED00"),
    )
    ax.set_title(ID_TO_NAME_SONIA[series_id])
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"sonia, {series_id}",
        df,
    )


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_ameribor(
    series_id: str = "AMERIBOR",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot American Interbank Offered Rate (AMERIBOR)

    Parameters
    ----------
    series_id: str
        FRED ID of AMERIBOR data to plot, options: ['AMERIBOR', 'AMBOR30T', 'AMBOR90T', 'AMBOR1W', 'AMBOR1M', 'AMBOR3M', 'AMBOR6M', 'AMBOR1Y', 'AMBOR2Y', 'AMBOR30', 'AMBOR90']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list)
    """
    df = fred_model.get_series_data(
        series_id=series_id, start_date=start_date, end_date=end_date
    )

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    colors = cycle(theme.get_colors())
    ax.plot(
        df.index,
        df.values,
        marker="o",
        linestyle="dashed",
        linewidth=2,
        markersize=4,
        color=next(colors, "#FCED00"),
    )
    ax.set_title(ID_TO_NAME_AMERIBOR[series_id])
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"ameribor, {series_id}",
        df,
    )


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_ffer(
    series_id: str = "FEDFUNDS",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot Federal Funds Effective Rate.

    A bank rate is the interest rate a nation's central bank charges to its domestic banks to borrow money. The rates
    central banks charge are set to stabilize the economy. In the United States, the Federal Reserve System's Board
    of Governors set the bank rate, also known as the discount rate.

    Parameters
    ----------
    series_id: str
        FRED ID of FFER data to plot, options: ['FEDFUNDS', 'DFF', 'FF', 'RIFSPFFNB', 'RIFSPFFNA', 'RIFSPFFNBWAW']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list)
    """
    df = fred_model.get_series_data(
        series_id=series_id, start_date=start_date, end_date=end_date
    )

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    colors = cycle(theme.get_colors())
    ax.plot(
        df.index,
        df.values,
        marker="o",
        linestyle="dashed",
        linewidth=2,
        markersize=4,
        color=next(colors, "#FCED00"),
    )
    ax.set_title(
        "Federal Funds Effective Rate " + ID_TO_NAME_FFER[series_id] + " [Percent]"
    )
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"ffer, {series_id}",
        df,
    )


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_fftr(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot Federal Funds Target Range.

    A bank rate is the interest rate a nation's central bank charges to its domestic banks to borrow money. The rates
    central banks charge are set to stabilize the economy. In the United States, the Federal Reserve System's Board
    of Governors set the bank rate, also known as the discount rate.

    Parameters
    ----------
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list)
    """
    df_upper = fred_model.get_series_data(
        series_id="DFEDTARU", start_date=start_date, end_date=end_date
    )
    df_lower = fred_model.get_series_data(
        series_id="DFEDTARL", start_date=start_date, end_date=end_date
    )
    df = pd.DataFrame([df_upper, df_lower]).transpose()

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
    )
    ax.set_title("Federal Funds Target Range [Percent]")
    ax.legend(["Upper limit", "Lower limit"])
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "fftr",
        df,
    )


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_effr(
    series_id: str = "EFFR",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot Effective Federal Funds Rate.

    A bank rate is the interest rate a nation's central bank charges to its domestic banks to borrow money. The rates
    central banks charge are set to stabilize the economy. In the United States, the Federal Reserve System's Board
    of Governors set the bank rate, also known as the discount rate.

    Parameters
    ----------
    series_id: str
        FRED ID of EFFER data to plot, options: ['EFFR', 'EFFRVOL', 'EFFR1', 'EFFR25', 'EFFR75', 'EFFR99']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list)
    """
    df = fred_model.get_series_data(
        series_id=series_id, start_date=start_date, end_date=end_date
    )

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    colors = cycle(theme.get_colors())
    ax.plot(
        df.index,
        df.values,
        marker="o",
        linestyle="dashed",
        linewidth=2,
        markersize=4,
        color=next(colors, "#FCED00"),
    )
    ax.set_title(ID_TO_NAME_EFFR[series_id])
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"effr, {series_id}",
        df,
    )


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_obfr(
    series_id: str = "OBFR",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot Overnight Bank Funding Rate (OBFR).

    A bank rate is the interest rate a nation's central bank charges to its domestic banks to borrow money. The rates
    central banks charge are set to stabilize the economy. In the United States, the Federal Reserve System's Board
    of Governors set the bank rate, also known as the discount rate.

    Parameters
    ----------
    series_id: str
        FRED ID of OBFR data to plot, options: ['OBFR', 'OBFRVOL', 'OBFR1', 'OBFR25', 'OBFR75', 'OBFR99']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list)
    """
    df = fred_model.get_series_data(
        series_id=series_id, start_date=start_date, end_date=end_date
    )

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    colors = cycle(theme.get_colors())
    ax.plot(
        df.index,
        df.values,
        marker="o",
        linestyle="dashed",
        linewidth=2,
        markersize=4,
        color=next(colors, "#FCED00"),
    )
    ax.set_title(ID_TO_NAME_OBFR[series_id])
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"obfr, {series_id}",
        df,
    )


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_iorb(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot Interest Rate on Reserve Balances.

    A bank rate is the interest rate a nation's central bank charges to its domestic banks to borrow money. The rates
    central banks charge are set to stabilize the economy. In the United States, the Federal Reserve System's Board
    of Governors set the bank rate, also known as the discount rate.

    Parameters
    ----------
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list)
    """
    df = fred_model.get_series_data(
        series_id="IORB", start_date=start_date, end_date=end_date
    )

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    colors = cycle(theme.get_colors())
    ax.plot(
        df.index,
        df.values,
        color=next(colors, "#FCED00"),
    )
    ax.set_title("Interest Rate on Reserve Balances [Percent]")
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "iorb",
        df,
    )


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_projection(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot FOMC Summary of Economic Projections for the Fed Funds Rate.

    A bank rate is the interest rate a nation's central bank charges to its domestic banks to borrow money. The rates
    central banks charge are set to stabilize the economy. In the United States, the Federal Reserve System's Board
    of Governors set the bank rate, also known as the discount rate.

    Parameters
    ----------
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list)
    """
    df_range_high = fred_model.get_series_data(
        series_id="FEDTARRH", start_date=start_date, end_date=end_date
    )
    df_central_tendency_high = fred_model.get_series_data(
        series_id="FEDTARCTH", start_date=start_date, end_date=end_date
    )
    df_median = fred_model.get_series_data(
        series_id="FEDTARMD", start_date=start_date, end_date=end_date
    )
    df_range_midpoint = fred_model.get_series_data(
        series_id="FEDTARRM", start_date=start_date, end_date=end_date
    )
    df_central_tendency_midpoint = fred_model.get_series_data(
        series_id="FEDTARCTM", start_date=start_date, end_date=end_date
    )
    df_range_low = fred_model.get_series_data(
        series_id="FEDTARRL", start_date=start_date, end_date=end_date
    )
    df_central_tendency_low = fred_model.get_series_data(
        series_id="FEDTARCTL", start_date=start_date, end_date=end_date
    )
    df = pd.DataFrame(
        [
            df_range_high,
            df_central_tendency_high,
            df_median,
            df_range_midpoint,
            df_central_tendency_midpoint,
            df_range_low,
            df_central_tendency_low,
        ]
    ).transpose()

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
    )
    ax.set_title(
        "FOMC Summary of Economic Projections for the Fed Funds Rate [Percent]"
    )
    ax.legend(
        [
            "Range High",
            "Central tendency High",
            "Median",
            "Range Midpoint",
            "Central tendency Midpoint",
            "Range Low",
            "Central tendency Low",
        ]
    )
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "projection",
        df,
    )


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_oldprojection(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot Longer Run FOMC Summary of Economic Projections for the Fed Funds Rate.

    A bank rate is the interest rate a nation's central bank charges to its domestic banks to borrow money. The rates
    central banks charge are set to stabilize the economy. In the United States, the Federal Reserve System's Board
    of Governors set the bank rate, also known as the discount rate.

    Parameters
    ----------
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list)
    """
    df_range_high = fred_model.get_series_data(
        series_id="FEDTARRHLR", start_date=start_date, end_date=end_date
    )
    df_central_tendency_high = fred_model.get_series_data(
        series_id="FEDTARCTHLR", start_date=start_date, end_date=end_date
    )
    df_median = fred_model.get_series_data(
        series_id="FEDTARMDLR", start_date=start_date, end_date=end_date
    )
    df_range_midpoint = fred_model.get_series_data(
        series_id="FEDTARRMLR", start_date=start_date, end_date=end_date
    )
    df_central_tendency_midpoint = fred_model.get_series_data(
        series_id="FEDTARCTMLR", start_date=start_date, end_date=end_date
    )
    df_range_low = fred_model.get_series_data(
        series_id="FEDTARRLLR", start_date=start_date, end_date=end_date
    )
    df_central_tendency_low = fred_model.get_series_data(
        series_id="FEDTARCTLLR", start_date=start_date, end_date=end_date
    )
    df = pd.DataFrame(
        [
            df_range_high,
            df_central_tendency_high,
            df_median,
            df_range_midpoint,
            df_central_tendency_midpoint,
            df_range_low,
            df_central_tendency_low,
        ]
    ).transpose()

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
    )
    ax.set_title(
        "Longer Run FOMC Summary of Economic Projections for the Fed Funds Rate [Percent]"
    )
    ax.legend(
        [
            "Range High",
            "Central tendency High",
            "Median",
            "Range Midpoint",
            "Central tendency Midpoint",
            "Range Low",
            "Central tendency Low",
        ]
    )
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "oldprojection",
        df,
    )


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_dwpcr(
    series_id: str = "DPCREDIT",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot Discount Window Primary Credit Rate.

    A bank rate is the interest rate a nation's central bank charges to its domestic banks to borrow money. The rates
    central banks charge are set to stabilize the economy. In the United States, the Federal Reserve System's Board
    of Governors set the bank rate, also known as the discount rate.

    Parameters
    ----------
    series_id: str
        FRED ID of DWPCR data to plot, options: ['MPCREDIT', 'RIFSRPF02ND', 'WPCREDIT', 'DPCREDIT', 'RIFSRPF02NA']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list)
    """
    df = fred_model.get_series_data(
        series_id=series_id, start_date=start_date, end_date=end_date
    )

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    colors = cycle(theme.get_colors())
    ax.plot(
        df.index,
        df.values,
        marker="o",
        linestyle="dashed",
        linewidth=2,
        markersize=4,
        color=next(colors, "#FCED00"),
    )
    ax.set_title(
        "Discount Window Primary Credit Rate "
        + ID_TO_NAME_DWPCR[series_id]
        + " [Percent]"
    )
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"dwpcr, {series_id}",
        df,
    )


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_ecbdfr(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot ECB Deposit Facility Rate for Euro Area.

    The deposit facility rate is one of the three interest rates the ECB sets every six weeks as part of its monetary
    policy. The rate defines the interest banks receive for depositing money with the central bank overnight.

    A bank rate is the interest rate a nation's central bank charges to its domestic banks to borrow money. The rates
    central banks charge are set to stabilize the economy.

    Parameters
    ----------
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list)
    """
    df = fred_model.get_series_data(
        series_id="ECBDFR", start_date=start_date, end_date=end_date
    )

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    colors = cycle(theme.get_colors())
    ax.plot(
        df.index,
        df.values,
        color=next(colors, "#FCED00"),
    )
    ax.set_title("ECB Deposit Facility Rate for Euro Area [Percent]")
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ecbdfr",
        df,
    )


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_ecbmlfr(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot ECB Marginal Lending Facility Rate for Euro Area.

    A standing facility of the Euro-system which counterparties may use to receive overnight credit from a national
    central bank at a pre-specified interest rate against eligible assets.

    A bank rate is the interest rate a nation's central bank charges to its domestic banks to borrow money. The rates
    central banks charge are set to stabilize the economy.

    Parameters
    ----------
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list)
    """
    df = fred_model.get_series_data(
        series_id="ECBMLFR", start_date=start_date, end_date=end_date
    )

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    colors = cycle(theme.get_colors())
    ax.plot(
        df.index,
        df.values,
        color=next(colors, "#FCED00"),
    )
    ax.set_title("ECB Marginal Lending Facility Rate for Euro Area [Percent]")
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ecbmlfr",
        df,
    )


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_ecbmrofr(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot ECB Marginal Lending Facility Rate for Euro Area.

    A regular open market operation executed by the Euro-system (in the form of a reverse transaction) for the purpose
    of providing the banking system with the amount of liquidity that the former deems to be appropriate. Main
    refinancing operations are conducted through weekly standard tenders (in which banks can bid for liquidity) and
    normally have a maturity of one week.

    A bank rate is the interest rate a nation's central bank charges to its domestic banks to borrow money. The rates
    central banks charge are set to stabilize the economy.

    Parameters
    ----------
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list)
    """
    df = fred_model.get_series_data(
        series_id="ECBMRRFR", start_date=start_date, end_date=end_date
    )

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    colors = cycle(theme.get_colors())
    ax.plot(
        df.index,
        df.values,
        color=next(colors, "#FCED00"),
    )
    ax.set_title(
        "ECB Main Refinancing Operations Rate: Fixed Rate Tenders for Euro Area [Percent]"
    )
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ecbmrofr",
        df,
    )


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_tmc(
    series_id: str = "T10Y3M",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot 10-Year Treasury Constant Maturity Minus Selected Treasury Constant Maturity data.

    Constant maturity is the theoretical value of a U.S. Treasury that is based on recent values of auctioned U.S.
    Treasuries. The value is obtained by the U.S. Treasury on a daily basis through interpolation of the Treasury
    yield curve which, in turn, is based on closing bid-yields of actively-traded Treasury securities.

    Parameters
    ----------
    series_id: str
        FRED ID of TMC data to plot, options: ['T10Y3M', 'T10Y3M']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list)
    """
    df = fred_model.get_series_data(
        series_id=series_id, start_date=start_date, end_date=end_date
    )

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    colors = cycle(theme.get_colors())
    ax.plot(
        df.index,
        df.values,
        marker="o",
        linestyle="dashed",
        linewidth=2,
        markersize=4,
        color=next(colors, "#FCED00"),
    )
    ax.set_title(
        "10-Year Treasury Constant Maturity Minus "
        + ID_TO_NAME_TMC[series_id]
        + " Treasury Constant Maturity [Percent]"
    )
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"tmc, {series_id}",
        df,
    )


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_ffrmc(
    series_id: str = "T10YFF",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot Selected Treasury Constant Maturity Minus Federal Funds Rate data.

    Constant maturity is the theoretical value of a U.S. Treasury that is based on recent values of auctioned U.S.
    Treasuries. The value is obtained by the U.S. Treasury on a daily basis through interpolation of the Treasury
    yield curve which, in turn, is based on closing bid-yields of actively-traded Treasury securities.

    Parameters
    ----------
    series_id: str
        FRED ID of FFRMC data to plot, options: ['T10YFF', 'T5YFF', 'T1YFF', 'T6MFF', 'T3MFF']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list)
    """
    df = fred_model.get_series_data(
        series_id=series_id, start_date=start_date, end_date=end_date
    )

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    colors = cycle(theme.get_colors())
    ax.plot(
        df.index,
        df.values,
        marker="o",
        linestyle="dashed",
        linewidth=2,
        markersize=4,
        color=next(colors, "#FCED00"),
    )
    ax.set_title(
        ID_TO_NAME_FFRMC[series_id]
        + " Treasury Constant Maturity Minus Federal Funds Rate [Percent]"
    )
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"ffrmc, {series_id}",
        df,
    )


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def display_yield_curve(
    date: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
    raw: bool = False,
    export: str = "",
):
    """Display yield curve based on US Treasury rates for a specified date.

    The graphic depiction of the relationship between the yield on bonds of the same credit quality but different
    maturities is known as the yield curve. In the past, most market participants have constructed yield curves from
    the observations of prices and yields in the Treasury market. Two reasons account for this tendency. First,
    Treasury securities are viewed as free of default risk, and differences in creditworthiness do not affect yield
    estimates. Second, as the most active bond market, the Treasury market offers the fewest problems of illiquidity
    or infrequent trading. The key function of the Treasury yield curve is to serve as a benchmark for pricing bonds
    and setting yields in other sectors of the debt market.

    It is clear that the market’s expectations of future rate changes are one important determinant of the
    yield-curve shape. For example, a steeply upward-sloping curve may indicate market expectations of near-term Fed
    tightening or of rising inflation. However, it may be too restrictive to assume that the yield differences across
    bonds with different maturities only reflect the market’s rate expectations. The well-known pure expectations
    hypothesis has such an extreme implication. The pure expectations hypothesis asserts that all government bonds
    have the same near-term expected return (as the nominally riskless short-term bond) because the return-seeking
    activity of risk-neutral traders removes all expected return differentials across bonds.

    Parameters
    ----------
    date: str
        Date to get curve for. If None, gets most recent date (format yyyy-mm-dd)
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    raw : bool
        Output only raw data
    export : str
        Export data to csv,json,xlsx or png,jpg,pdf,svg file
    """
    rates, date_of_yield = fred_model.get_yield_curve(date, True)
    if rates.empty:
        console.print(f"[red]Yield data not found for {date_of_yield}.[/red]\n")
        return
    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    ax.plot(rates["Maturity"], rates["Rate"], "-o")
    ax.set_xlabel("Maturity")
    ax.set_ylabel("Rate (%)")
    theme.style_primary_axis(ax)
    if external_axes is None:
        ax.set_title(f"US Yield Curve for {date_of_yield} ")
        theme.visualize_output()

    if raw:
        print_rich_table(
            rates,
            headers=list(rates.columns),
            show_index=False,
            title=f"United States Yield Curve for {date_of_yield}",
            floatfmt=".3f",
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ycrv",
        rates,
    )


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def display_inflation_indexed_yield_curve(
    date: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
    raw: bool = False,
    export: str = "",
):
    """Display inflation-indexed yield curve based on US Treasury rates for a specified date.

    The graphic depiction of the relationship between the yield on bonds of the same credit quality but different
    maturities is known as the yield curve. In the past, most market participants have constructed yield curves from
    the observations of prices and yields in the Treasury market. Two reasons account for this tendency. First,
    Treasury securities are viewed as free of default risk, and differences in creditworthiness do not affect yield
    estimates. Second, as the most active bond market, the Treasury market offers the fewest problems of illiquidity
    or infrequent trading. The key function of the Treasury yield curve is to serve as a benchmark for pricing bonds
    and setting yields in other sectors of the debt market.

    It is clear that the market’s expectations of future rate changes are one important determinant of the
    yield-curve shape. For example, a steeply upward-sloping curve may indicate market expectations of near-term Fed
    tightening or of rising inflation. However, it may be too restrictive to assume that the yield differences across
    bonds with different maturities only reflect the market’s rate expectations. The well-known pure expectations
    hypothesis has such an extreme implication. The pure expectations hypothesis asserts that all government bonds
    have the same near-term expected return (as the nominally riskless short-term bond) because the return-seeking
    activity of risk-neutral traders removes all expected return differentials across bonds.

    Parameters
    ----------
    date: str
        Date to get curve for. If None, gets most recent date (format yyyy-mm-dd)
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    raw : bool
        Output only raw data
    export : str
        Export data to csv,json,xlsx or png,jpg,pdf,svg file
    """
    rates, date_of_yield = fred_model.get_inflation_indexed_yield_curve(date, True)
    if rates.empty:
        console.print(f"[red]Yield data not found for {date_of_yield}.[/red]\n")
        return
    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    ax.plot(rates["Maturity"], rates["Rate"], "-o")
    ax.set_xlabel("Maturity")
    ax.set_ylabel("Rate (%)")
    theme.style_primary_axis(ax)
    if external_axes is None:
        ax.set_title(f"US Yield Curve for {date_of_yield} ")
        theme.visualize_output()

    if raw:
        print_rich_table(
            rates,
            headers=list(rates.columns),
            show_index=False,
            title=f"United States Yield Curve for {date_of_yield}",
            floatfmt=".3f",
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "iiycrv",
        rates,
    )


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_tbill(
    series_id: str = "TB3MS",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot Treasury Bill Secondary Market Rate.

    A Treasury Bill (T-Bill) is a short-term U.S. government debt obligation backed by the Treasury Department with a
    maturity of one year or less. Treasury bills are usually sold in denominations of $1,000. However, some can reach
    a maximum denomination of $5 million in non-competitive bids. These securities are widely regarded as low-risk
    and secure investments.

    Parameters
    ----------
    series_id: str
        FRED ID of Treasury Bill Secondary Market Rate data to plot, options: ['TB3MS', 'DTB4WK', 'DTB1YR', 'DTB6']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list)
    """
    df = fred_model.get_series_data(
        series_id=series_id, start_date=start_date, end_date=end_date
    )

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    colors = cycle(theme.get_colors())
    ax.plot(
        df.index,
        df.values,
        marker="o",
        linestyle="dashed",
        linewidth=2,
        markersize=4,
        color=next(colors, "#FCED00"),
    )
    ax.set_title(f"{ID_TO_NAME_SECONDARY[series_id]} Treasury Bill Secondary Market Rate, Discount Basis [Percent]")
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"tbill, {series_id}",
        df,
    )


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_cmn(
    series_id: str = "DGS10",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
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
    series_id: str
        FRED ID of Treasury Constant Maturity Nominal Market Yield data to plot, options: ['DGS1MO', 'DGS3MO', 'DGS6MO', 'DGS1', 'DGS2', 'DGS3', 'DGS5', 'DGS7', 'DGS10', 'DGS20', DGS30']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list)
    """
    df = fred_model.get_series_data(
        series_id=series_id, start_date=start_date, end_date=end_date
    )

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    colors = cycle(theme.get_colors())
    ax.plot(
        df.index,
        df.values,
        marker="o",
        linestyle="dashed",
        linewidth=2,
        markersize=4,
        color=next(colors, "#FCED00"),
    )
    ax.set_title(f"{ID_TO_NAME_CMN[series_id]}  Treasury Constant Maturity Nominal Market Yield [Percent]")
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"cmn, {series_id}",
        df,
    )


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_tips(
    series_id: str = "DFII10",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot Plot Yields on Treasury inflation protected securities (TIPS) adjusted to constant maturities.

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
    series_id: str
        FRED ID of TIPS adjusted to constant maturities data to plot, options: ['DFII5', 'DFII7', 'DFII10', 'DFII20', 'DFII30']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list)
    """
    df = fred_model.get_series_data(
        series_id=series_id, start_date=start_date, end_date=end_date
    )

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    colors = cycle(theme.get_colors())
    ax.plot(
        df.index,
        df.values,
        marker="o",
        linestyle="dashed",
        linewidth=2,
        markersize=4,
        color=next(colors, "#FCED00"),
    )
    ax.set_title(f"{ID_TO_NAME_TIPS[series_id]}  Yields on Treasury inflation protected securities (TIPS) adjusted to "
                 f"constant maturities [Percent]")
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"tips, {series_id}",
        df,
    )


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_tbffr(
    series_id: str = "TB3SMFFM",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot Selected Treasury Bill Minus Federal Funds Rate data.

    Parameters
    ----------
    series_id: str
        FRED ID of TBFFR data to plot, options: ['TB3SMFFM', 'TB6SMFFM']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list)
    """
    df = fred_model.get_series_data(
        series_id=series_id, start_date=start_date, end_date=end_date
    )

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    colors = cycle(theme.get_colors())
    ax.plot(
        df.index,
        df.values,
        marker="o",
        linestyle="dashed",
        linewidth=2,
        markersize=4,
        color=next(colors, "#FCED00"),
    )
    ax.set_title(
        ID_TO_NAME_TBFFR[series_id]
        + " Treasury Bill Minus Federal Funds Rate [Percent]"
    )
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"tbffr, {series_id}",
        df,
    )
