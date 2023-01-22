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
)
from openbb_terminal.fixedincome.fred_model import get_series_data

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
    df = get_series_data(series_id=series_id, start_date=start_date, end_date=end_date)

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
    df = get_series_data(series_id=series_id, start_date=start_date, end_date=end_date)

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
    df = get_series_data(series_id=series_id, start_date=start_date, end_date=end_date)

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
    df = get_series_data(series_id=series_id, start_date=start_date, end_date=end_date)

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
    df = get_series_data(series_id=series_id, start_date=start_date, end_date=end_date)

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
    df_upper = get_series_data(
        series_id="DFEDTARU", start_date=start_date, end_date=end_date
    )
    df_lower = get_series_data(
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
    df = get_series_data(series_id=series_id, start_date=start_date, end_date=end_date)

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
    df = get_series_data(series_id=series_id, start_date=start_date, end_date=end_date)

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
    df = get_series_data(series_id="IORB", start_date=start_date, end_date=end_date)

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
    df_range_high = get_series_data(
        series_id="FEDTARRH", start_date=start_date, end_date=end_date
    )
    df_central_tendency_high = get_series_data(
        series_id="FEDTARCTH", start_date=start_date, end_date=end_date
    )
    df_median = get_series_data(
        series_id="FEDTARMD", start_date=start_date, end_date=end_date
    )
    df_range_midpoint = get_series_data(
        series_id="FEDTARRM", start_date=start_date, end_date=end_date
    )
    df_central_tendency_midpoint = get_series_data(
        series_id="FEDTARCTM", start_date=start_date, end_date=end_date
    )
    df_range_low = get_series_data(
        series_id="FEDTARRL", start_date=start_date, end_date=end_date
    )
    df_central_tendency_low = get_series_data(
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
    df_range_high = get_series_data(
        series_id="FEDTARRHLR", start_date=start_date, end_date=end_date
    )
    df_central_tendency_high = get_series_data(
        series_id="FEDTARCTHLR", start_date=start_date, end_date=end_date
    )
    df_median = get_series_data(
        series_id="FEDTARMDLR", start_date=start_date, end_date=end_date
    )
    df_range_midpoint = get_series_data(
        series_id="FEDTARRMLR", start_date=start_date, end_date=end_date
    )
    df_central_tendency_midpoint = get_series_data(
        series_id="FEDTARCTMLR", start_date=start_date, end_date=end_date
    )
    df_range_low = get_series_data(
        series_id="FEDTARRLLR", start_date=start_date, end_date=end_date
    )
    df_central_tendency_low = get_series_data(
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
    df = get_series_data(series_id=series_id, start_date=start_date, end_date=end_date)

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
