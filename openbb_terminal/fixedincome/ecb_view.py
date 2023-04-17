""" ECB view """
__docformat__ = "numpy"

# IMPORTATION STANDARD
import logging
import os
from typing import Optional

# IMPORTATION THIRDPARTY
import pandas as pd

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.fixedincome import ecb_model
from openbb_terminal.helper_funcs import export_data, print_rich_table
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
    external_axes: bool = False,
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
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    series_id = ESTR_PARAMETER_TO_ECB_ID.get(parameter, "")

    df = ecb_model.get_series_data(
        series_id, start_date if start_date else "", end_date if end_date else ""
    )

    fig = OpenBBFigure()
    fig.set_title(ID_TO_NAME[series_id])

    fig.add_scatter(x=df.index, y=df.values, name=series_id, mode="lines")

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
            fig,
        )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_ecb_yield_curve(
    date: str = "",
    yield_type: str = "spot_rate",
    detailed: bool = False,
    any_rating: bool = True,
    external_axes: bool = False,
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
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    raw : bool
        Output only raw data
    export : str
        Export data to csv,json,xlsx or png,jpg,pdf,svg file
    """
    rates, date_of_yield = ecb_model.get_ecb_yield_curve(
        date, yield_type, True, detailed, any_rating
    )
    if rates.empty:
        return console.print(f"[red]Yield data not found for {date_of_yield}.[/red]\n")

    fig = OpenBBFigure(xaxis_title="Maturity", yaxis_title="Rate (%)")
    fig.set_title(
        f"Euro Area{' AAA Bonds' if not any_rating else ' All Bonds'} {yield_type.replace('_', ' ').title()} "
        f"Yield Curve for {date_of_yield}",
    )

    fig.add_scatter(x=rates["Maturity"], y=rates["Rate"], name="Yield")

    if raw:
        print_rich_table(
            rates,
            headers=list(rates.columns),
            show_index=False,
            title=f"Euro Area{' AAA Bonds' if not any_rating else ' All Bonds'} {yield_type.replace('_', ' ').title()} "
            f"Yield Curve for {date_of_yield}",
            floatfmt=".3f",
            export=bool(export),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ecbycrv",
        rates / 100,
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)
