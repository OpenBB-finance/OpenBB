""" ECB view """
__docformat__ = "numpy"

import logging
import os
from itertools import cycle
from typing import List, Optional

import pandas as pd
from matplotlib import pyplot as plt

from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.fixedincome import ecb_model
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

# pylint: disable=too-many-function-args

ID_TO_NAME = {
    "EST.B.EU000A2X2A25.WT": "Euro Short-Term Rate: Volume-Weighted Trimmed Mean Rate [Percent]",
    "EST.B.EU000A2X2A25.TT": "Euro Short-Term Rate: Total Volume [Millions of EUR]",
    "EST.B.EU000A2X2A25.NT": "Euro Short-Term Rate: Number of Transactions",
    "EST.B.EU000A2X2A25.R75": "Euro Short-Term Rate: Rate at 75th Percentile of Volume [Percent]",
    "EST.B.EU000A2X2A25.NB": "Euro Short-Term Rate: Number of Active Banks",
    "EST.B.EU000A2X2A25.VL": "Euro Short-Term Rate: Share of Volume of the 5 Largest Active Banks [Percent]",
    "EST.B.EU000A2X2A25.R25": "Euro Short-Term Rate: Rate at 25th Percentile of Volume [Percent]",
}

ESTR_PARAMETER_TO_ECB_ID = {
    "volume_weighted_trimmed_mean_rate": "EST.B.EU000A2X2A25.WT",
    "number_of_transactions": "EST.B.EU000A2X2A25.NT",
    "number_of_active_banks": "EST.B.EU000A2X2A25.NB",
    "total_volume": "EST.B.EU000A2X2A25.TT",
    "share_of_volume_of_the_5_largest_active_banks": "EST.B.EU000A2X2A25.VL",
    "rate_at_75th_percentile_of_volume": "EST.B.EU000A2X2A25.R75",
    "rate_at_25th_percentile_of_volume": "EST.B.EU000A2X2A25.R25",
}


@log_start_end(log=logger)
def plot_estr(
    parameter: str = "EST.B.EU000A2X2A25.WT",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    sheet_name: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot Euro Short-Term Rate (ESTR)

    Parameters
    ----------
    series_id: str
        ECB ID of ESTR data to plot, options: ['EST.B.EU000A2X2A25.WT', 'EST.B.EU000A2X2A25.TT',
        'EST.B.EU000A2X2A25.NT', 'EST.B.EU000A2X2A25.R75', 'EST.B.EU000A2X2A25.NB',
        'EST.B.EU000A2X2A25.VL', 'EST.B.EU000A2X2A25.R25']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list)
    """
    series_id = ESTR_PARAMETER_TO_ECB_ID.get(parameter, "")

    df = ecb_model.get_series_data(
        series_id, start_date if start_date else "", end_date if end_date else ""
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
    ax.set_title(ID_TO_NAME[series_id])
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    if export:
        if "[Percent]" in ID_TO_NAME[series_id]:
            # Check whether it is a percentage, relevant for exporting
            df_transformed = pd.DataFrame(df, columns=[series_id]) / 100
        else:
            df_transformed = pd.DataFrame(df, columns=[series_id])

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            series_id,
            df_transformed,
            sheet_name,
        )


@log_start_end(log=logger)
def display_ecb_yield_curve(
    date: str = "",
    yield_type: str = "spot_rate",
    detailed: bool = False,
    any_rating: bool = True,
    external_axes: Optional[List[plt.Axes]] = None,
    raw: bool = False,
    export: str = "",
    sheet_name: str = "",
):
    """Display yield curve based on ECB Treasury rates for a specified date.

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
    yield_type: str
        What type of yield curve to get, options: ['spot_rate', 'instantaneous_forward', 'par_yield']
    detailed: bool
        If True, returns detailed data. Note that this is very slow.
    aaa_only: bool
        If True, it only returns rates for AAA rated bonds. If False, it returns rates for all bonds
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    raw : bool
        Output only raw data
    export : str
        Export data to csv,json,xlsx or png,jpg,pdf,svg file
    """
    rates, date_of_yield = ecb_model.get_ecb_yield_curve(
        date, yield_type, True, detailed, any_rating
    )
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
        ax.set_title(
            f"Euro Area{' AAA Bonds' if not any_rating else ' All Bonds'} {yield_type.replace('_', ' ').title()} "
            f"Yield Curve for {date_of_yield}",
            fontsize=15,
        )
        theme.visualize_output()

    if raw:
        print_rich_table(
            rates,
            headers=list(rates.columns),
            show_index=False,
            title=f"Euro Area{' AAA Bonds' if not any_rating else ' All Bonds'} {yield_type.replace('_', ' ').title()} "
            f"Yield Curve for {date_of_yield}",
            floatfmt=".3f",
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ecbycrv",
        rates / 100,
        sheet_name,
    )
