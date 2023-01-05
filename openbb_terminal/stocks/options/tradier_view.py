"""Tradier options view"""
__docformat__ = "numpy"

import argparse
import logging
import os
import warnings
from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd

from openbb_terminal import rich_config
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    lambda_long_number_format_y_axis,
    patch_pandas_text_adjustment,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.options import tradier_model, yfinance_model

logger = logging.getLogger(__name__)

column_map = {"mid_iv": "iv", "open_interest": "oi", "volume": "vol"}
warnings.filterwarnings("ignore")


def get_strike_bounds(
    options: pd.DataFrame, current_price: float, min_sp: float, max_sp: float
) -> Tuple[float, float]:
    if min_sp == -1:
        if current_price == 0:
            min_strike = options["strike"].iat[0]
        else:
            min_strike = 0.75 * current_price
    else:
        min_strike = min_sp

    if max_sp == -1:
        if current_price == 0:
            max_strike = options["strike"].iat[-1]
        else:
            max_strike = 1.25 * current_price
    else:
        max_strike = max_sp
    return min_strike, max_strike


def lambda_red_highlight(val) -> str:
    """Red highlight

    Parameters
    ----------
    val
        dataframe values to color

    Returns
    -------
    str
        colored dataframes values
    """
    return f"[red]{val}[/red]"


def lambda_green_highlight(val) -> str:
    """Green highlight

    Parameters
    ----------
    values : List[str]
        dataframe values to color

    Returns
    -------
    List[str]
        colored dataframes values
    """
    return f"[green]{val}[/green]"


@log_start_end(log=logger)
def check_valid_option_chains_headers(headers: str) -> List[str]:
    """Check valid option chains headers

    Parameters
    ----------
    headers : str
        Option chains headers

    Returns
    -------
    List[str]
        List of columns string
    """
    columns = [str(item) for item in headers.split(",")]

    for header in columns:
        if header not in tradier_model.df_columns:
            raise argparse.ArgumentTypeError("Invalid option chains header selected!")

    return columns


@log_start_end(log=logger)
def display_expirations(ticker: str, source: str = "YahooFinance"):
    """Displays the expirations for a ticker

    Parameters
    ----------
    ticker: str
        The ticker to look up
    source: str
        Where to get the data from. Options: yf (yahoo finance) or tr (tradier)
    """
    if source == "YahooFinance":
        exps = yfinance_model.option_expirations(ticker)
    elif source == "Tradier":
        exps = tradier_model.option_expirations(ticker)
    else:
        raise ValueError("Invalid source. Please select 'yf' or 'tr'")
    display_expiry_dates(exps)


@log_start_end(log=logger)
def display_expiry_dates(expiry_dates: list):
    """Display expiry dates

    Parameters
    ----------
    expiry_dates: list
        The expiry dates of the chosen ticker.
    """
    expiry_dates_df = pd.DataFrame(expiry_dates, columns=["Date"])

    print_rich_table(
        expiry_dates_df,
        headers=list(expiry_dates_df.columns),
        title="Available expiry dates",
        show_index=True,
        index_name="Identifier",
    )


@log_start_end(log=logger)
def display_chains(
    symbol: str,
    expiry: str,
    to_display: List[str] = None,
    min_sp: float = -1,
    max_sp: float = -1,
    calls_only: bool = False,
    puts_only: bool = False,
    export: str = "",
):
    """Display option chain

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    expiry: str
        Expiration date of option
    to_display: List[str]
        List of columns to display
    min_sp: float
        Min strike price to display
    max_sp: float
        Max strike price to display
    calls_only: bool
        Only display calls
    puts_only: bool
        Only display puts
    export: str
        Format to  export file
    """

    if to_display is None:
        to_display = tradier_model.default_columns

    chains_df = tradier_model.get_option_chain(symbol, expiry)

    if isinstance(chains_df, pd.DataFrame) and not chains_df.empty:

        columns = to_display + ["strike", "option_type"]
        chains_df = chains_df[columns].rename(columns=column_map)

        min_strike, max_strike = get_strike_bounds(chains_df, 0, min_sp, max_sp)

        chains_df = chains_df[chains_df["strike"] >= min_strike]
        chains_df = chains_df[chains_df["strike"] <= max_strike]

        calls_df = chains_df[chains_df.option_type == "call"].drop(
            columns=["option_type"]
        )
        puts_df = chains_df[chains_df.option_type == "put"].drop(
            columns=["option_type"]
        )

        df = calls_df if calls_only else puts_df

        if calls_only or puts_only:
            print_rich_table(
                df,
                headers=[x.title() for x in df.columns],
                show_index=False,
                title=f"The strike prices are displayed between {min_strike} and {max_strike}",
            )

        else:
            puts_df = puts_df[puts_df.columns[::-1]]
            chain_table = calls_df.merge(puts_df, on="strike")

            if rich_config.USE_COLOR:
                call_cols = [col for col in chain_table if col.endswith("_x")]
                put_cols = [col for col in chain_table if col.endswith("_y")]
                patch_pandas_text_adjustment()
                pd.set_option("display.max_colwidth", 0)
                pd.set_option("display.max_rows", None)
                for cc in call_cols:
                    chain_table[cc] = (
                        chain_table[cc].astype(str).apply(lambda_green_highlight)
                    )
                for pc in put_cols:
                    chain_table[pc] = (
                        chain_table[pc].astype(str).apply(lambda_red_highlight)
                    )
            headers = [
                col.strip("_x")
                if col.endswith("_x")
                else col.strip("_y")
                if col.endswith("_y")
                else col
                for col in chain_table.columns
            ]
            print_rich_table(
                chain_table,
                headers=headers,
                show_index=False,
                title=f"{symbol} Option chain for {expiry}",
            )

        export_data(
            export,
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "chains",
            chains_df,
        )


@log_start_end(log=logger)
def display_historical(
    symbol: str,
    expiry: str,
    strike: float = 0,
    put: bool = False,
    raw: bool = False,
    chain_id: str = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot historical option prices

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    expiry: str
        Expiry date of option
    strike: float
        Option strike price
    put: bool
        Is this a put option?
    raw: bool
        Print raw data
    chain_id: str
        OCC option symbol
    export: str
        Format of export file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    df_hist = tradier_model.get_historical_options(
        symbol, expiry, strike, put, chain_id
    )

    if raw:
        print_rich_table(
            df_hist,
            headers=[x.title() for x in df_hist.columns],
            title="Historical Option Prices",
        )

    op_type = ["call", "put"][put]

    candle_chart_kwargs = {
        "type": "candle",
        "style": theme.mpf_style,
        "volume": True,
        "xrotation": theme.xticks_rotation,
        "scale_padding": {"left": 0.3, "right": 1.2, "top": 0.8, "bottom": 0.8},
        "update_width_config": {
            "candle_linewidth": 0.6,
            "candle_width": 0.8,
            "volume_linewidth": 0.8,
            "volume_width": 0.8,
        },
        "datetime_format": "%Y-%b-%d",
    }
    if external_axes is None:
        candle_chart_kwargs["returnfig"] = True
        candle_chart_kwargs["figratio"] = (10, 7)
        candle_chart_kwargs["figscale"] = 1.10
        candle_chart_kwargs["figsize"] = plot_autoscale()
        fig, ax = mpf.plot(df_hist, **candle_chart_kwargs)
        fig.suptitle(
            f"Historical {strike} {op_type.title()}",
            x=0.055,
            y=0.965,
            horizontalalignment="left",
        )
        lambda_long_number_format_y_axis(df_hist, "volume", ax)
        theme.visualize_output(force_tight_layout=False)
    elif is_valid_axes_count(external_axes, 2):
        (ax1, ax2) = external_axes
        candle_chart_kwargs["ax"] = ax1
        candle_chart_kwargs["volume"] = ax2
        mpf.plot(df_hist, **candle_chart_kwargs)
    else:
        return

    console.print()

    if export:
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "hist",
            df_hist,
        )
