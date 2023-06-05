# IMPORTATION STANDARD
import logging
import os

# IMPORTATION THIRDPARTY
from typing import Optional, Tuple

import pandas as pd

from openbb_terminal import OpenBBFigure
from openbb_terminal.core.plots.backend import plots_backend

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.options.op_helpers import (
    calculate_max_pain,
    get_greeks,
    get_strikes,
)

logger = logging.getLogger(__name__)

# pylint: disable=C0302,R0913


def get_calls_and_puts(chain: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    calls = chain[chain["optionType"] == "call"]
    puts = chain[chain["optionType"] == "put"]
    return calls, puts


def get_max_pain(calls: pd.DataFrame, puts: pd.DataFrame) -> float:
    call_oi = calls.set_index("strike")["openInterest"]
    put_oi = puts.set_index("strike")["openInterest"]
    df_opt = pd.merge(call_oi, put_oi, left_index=True, right_index=True)
    df_opt = df_opt.rename(
        columns={"openInterest_x": "OI_call", "openInterest_y": "OI_put"}
    )
    return calculate_max_pain(df_opt)


def print_raw(
    calls: pd.DataFrame,
    puts: pd.DataFrame,
    title: str,
    calls_only: bool = False,
    puts_only: bool = False,
    export: str = "",
):
    current_user = get_current_user()
    enable_interactive = (
        current_user.preferences.USE_INTERACTIVE_DF and plots_backend().isatty
    )

    if enable_interactive:
        table_title = f"{title} - Calls & Puts"
        data = pd.concat([calls, puts])

        if calls_only or puts_only:
            options_type = "call" if calls_only else "put"
            data = data[data["optionType"] == options_type].drop(columns=["optionType"])
            table_title = f"{title} - {options_type.title()}s"

        return print_rich_table(
            data,
            headers=list(data.columns),
            show_index=False,
            title=table_title,
            export=bool(export),
            floatfmt=".6f",
        )

    for opt_type, only in zip(["call", "put"], [puts_only, calls_only]):
        if not only:
            data = (calls if opt_type == "call" else puts).drop(columns=["optionType"])
            print_rich_table(
                data,
                headers=list(data.columns),
                show_index=False,
                title=f"{title} - {opt_type.title()}s",
                export=bool(export),
                floatfmt=".4f",
            )

    return None


@log_start_end(log=logger)
def plot_vol(
    chain: pd.DataFrame,
    current_price: float,
    symbol: str,
    expiry: str,
    min_sp: float = -1,
    max_sp: float = -1,
    calls_only: bool = False,
    puts_only: bool = False,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
):
    """Plot volume

    Parameters
    ----------
    chain: pd.Dataframe
        Dataframe with options chain
    current_price: float
        Current price of selected symbol
    symbol: str
        Ticker symbol
    expiry: str
        expiration date for options
    min_sp: float
        Min strike to consider
    max_sp: float
        Max strike to consider
    calls_only: bool
        Show calls only
    puts_only: bool
        Show puts only
    export: str
        Format to export file
    sheet_name: str
        Optionally specify the name of the sheet to export to
    external_axes : bool, optional
        Whether to return the figure object or not, by default False


    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> aapl_chain_data = openbb.stocks.options.chains("AAPL", expiration="2023-07-21", source="Nasdaq")
    >>> aapl_price = openbb.stocks.options.price("AAPL", source="Nasdaq")
    >>> openbb.stocks.options.vol(
            chain=aapl_chain_data,
            symbol="AAPL",
            current_price=aapl_price,
            expiry="2023-07-21",
        )
    """
    calls, puts = get_calls_and_puts(chain)

    min_strike, max_strike = get_strikes(min_sp, max_sp, chain)
    title = f"Volume for {symbol.upper()} expiring {expiry}"

    if raw:
        print_raw(calls, puts, title, calls_only, puts_only, export=export)

    fig = OpenBBFigure(
        xaxis=dict(title="Strike Price", range=[min_strike, max_strike]),
        yaxis_title="Volume",
    )
    fig.set_title(title)

    if not puts_only:
        call_v = calls.set_index("strike")["volume"]
        fig.add_scatter(
            x=call_v.index, y=call_v.values, mode="lines+markers", name="Calls"
        )
    if not calls_only:
        put_v = puts.set_index("strike")["volume"]
        fig.add_scatter(
            x=put_v.index, y=put_v.values, mode="lines+markers", name="Puts"
        )

    fig.add_vline(x=current_price, line_dash="dash", line_width=2, name="Current Price")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"vol_{symbol}_{expiry}",
        chain,
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)


@log_start_end(log=logger)
def plot_oi(
    chain: pd.DataFrame,
    current_price: float,
    symbol: str,
    expiry: str,
    min_sp: float = -1,
    max_sp: float = -1,
    calls_only: bool = False,
    puts_only: bool = False,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
):
    """Plot open interest

    Parameters
    ----------
    chain: pd.Dataframe
        Dataframe with options chain
    current_price: float
        Current price of selected symbol
    symbol: str
        Ticker symbol
    expiry: str
        expiration date for options
    min_sp: float
        Min strike to consider
    max_sp: float
        Max strike to consider
    calls_only: bool
        Show calls only
    puts_only: bool
        Show puts only
    export: str
        Format to export file
    sheet_name: str
        Optionally specify the name of the sheet to export to
    external_axes : bool, optional
        Whether to return the figure object or not, by default False

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> aapl_chain_data = openbb.stocks.options.chains("AAPL", expiration="2023-07-21", source="Nasdaq")
    >>> aapl_price = openbb.stocks.options.price("AAPL", source="Nasdaq")
    >>> openbb.stocks.options.oi(
            chain=aapl_chain_data,
            symbol="AAPL",
            current_price=aapl_price,
            expiry="2023-07-21",
        )
    """
    calls, puts = get_calls_and_puts(chain)

    min_strike, max_strike = get_strikes(min_sp, max_sp, chain)
    max_pain = get_max_pain(calls, puts)
    title = f"Open Interest for {symbol.upper()} expiring {expiry}"

    if raw:
        print_raw(calls, puts, title, calls_only, puts_only, export=export)

    fig = OpenBBFigure(
        xaxis=dict(title="Strike Price", range=[min_strike, max_strike]),
        yaxis_title="Open Interest",
    )
    fig.set_title(title)

    if not puts_only:
        call_oi = calls.set_index("strike")["openInterest"]
        fig.add_scatter(
            x=call_oi.index, y=call_oi.values, mode="lines+markers", name="Calls"
        )
    if not calls_only:
        put_oi = puts.set_index("strike")["openInterest"]
        fig.add_scatter(
            x=put_oi.index, y=put_oi.values, mode="lines+markers", name="Puts"
        )

    fig.add_vline_legend(
        x=current_price,
        name="Current Price",
        line=dict(dash="dash", width=2, color="grey"),
    )
    fig.add_vline_legend(
        x=max_pain,
        name=f"Max Pain: {max_pain}",
        line=dict(dash="dash", width=2, color="white"),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"oi_{symbol}_{expiry}",
        chain,
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)


@log_start_end(log=logger)
def plot_voi(
    chain: pd.DataFrame,
    current_price: float,
    symbol: str,
    expiry: str,
    min_sp: float = -1,
    max_sp: float = -1,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
):
    """Plot volume and open interest

    Parameters
    ----------
    chain: pd.Dataframe
        Dataframe with options chain
    current_price: float
        Current price of selected symbol
    symbol: str
        Stock ticker symbol
    expiry: str
        Option expiration
    min_sp: float
        Min strike price
    max_sp: float
        Max strike price
    export: str
        Format for exporting data
    sheet_name: str
        Optionally specify the name of the sheet to export to
    external_axes : bool, optional
        Whether to return the figure object or not, by default False

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> aapl_chain_data = openbb.stocks.options.chains("AAPL", expiration="2023-07-21", source="Nasdaq")
    >>> aapl_price = openbb.stocks.options.price("AAPL", source="Nasdaq")
    >>> openbb.stocks.options.voi(
            chain=aapl_chain_data,
            symbol="AAPL",
            current_price=aapl_price,
            expiry="2023-07-21",
        )
    """
    get_current_user()
    calls, puts = get_calls_and_puts(chain)

    min_strike, max_strike = get_strikes(min_sp, max_sp, chain)
    max_pain = get_max_pain(calls, puts)
    title = f"Volume and Open Interest for {symbol.upper()} expiring {expiry}"

    option_chain = pd.merge(
        calls[["volume", "strike", "openInterest"]],
        puts[["volume", "strike", "openInterest"]],
        on="strike",
    )

    option_chain = option_chain.rename(
        columns={
            "volume_x": "volume_call",
            "volume_y": "volume_put",
            "openInterest_x": "openInterest_call",
            "openInterest_y": "openInterest_put",
        }
    )

    option_chain[["openInterest_put", "volume_put"]] = (
        option_chain[["openInterest_put", "volume_put"]] * -1
    )
    option_chain[["openInterest_call", "volume_call"]] = option_chain[
        ["openInterest_call", "volume_call"]
    ]

    fig = OpenBBFigure(yaxis_title="Volume", xaxis_title="Strike Price")
    fig.set_title(title)

    option_chain = option_chain[
        (option_chain.strike >= min_strike) & (option_chain.strike <= max_strike)
    ]
    fig.add_bar(
        x=option_chain.strike,
        y=option_chain.openInterest_call,
        name="Calls: Open Interest",
        marker_color="lightgreen",
        hovertemplate="Calls Open Interest: %{y}<extra></extra>",
    )
    fig.add_bar(
        x=option_chain.strike,
        y=option_chain.volume_call,
        name="Calls: Volume",
        marker_color="green",
        hovertemplate="Calls Volume: %{y}<extra></extra>",
    )
    fig.add_bar(
        x=option_chain.strike,
        y=option_chain.openInterest_put,
        name="Puts: Open Interest",
        marker_color="pink",
        hovertemplate="Puts Open Interest: %{y}<extra></extra>",
    )
    fig.add_bar(
        x=option_chain.strike,
        y=option_chain.volume_put,
        name="Puts: Volume",
        marker_color="red",
        hovertemplate="Puts Volume: %{y}<extra></extra>",
    )
    fig.add_vline_legend(
        x=current_price,
        name="Current stock price",
        line=dict(dash="dash", width=2, color="white"),
    )
    fig.add_vline_legend(
        x=max_pain,
        name=f"Max pain = {max_pain}",
        line=dict(dash="dash", width=2, color="red"),
    )

    fig.update_layout(barmode="relative", hovermode="x unified")

    if raw:
        print_raw(calls, puts, title, export=export)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"voi_{symbol}_{expiry}",
        chain,
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)


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
    chain: pd.DataFrame,
    expire: str,
    current_price: float = 0,
    calls_only: bool = False,
    puts_only: bool = False,
    min_sp: float = -1,
    max_sp: float = -1,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Display chains

    chain: pd.Dataframe
        Dataframe with options chain
    current_price: float
        Current price of selected symbol
    expire: str
        The date of expiration
    min_sp: float
        Min strike price
    max_sp: float
        Max strike price
    calls_only: bool
        Show calls only
    puts_only: bool
        Show puts only
    export: str
        Format for exporting data
    sheet_name: str
        Optionally specify the name of the sheet to export to
    """
    min_strike, max_strike = get_strikes(min_sp, max_sp, chain)

    chain = chain[chain["strike"] >= min_strike]
    chain = chain[chain["strike"] <= max_strike]

    calls, puts = get_calls_and_puts(chain)
    # Tradier provides the greeks, so calculate them if they are not present
    if "delta" not in chain.columns:
        if "impliedVolatility" in chain.columns:
            chain = get_greeks(
                current_price=current_price,
                calls=calls,
                expire=expire,
                puts=puts,
                show_all=True,
            )
            # if the greeks calculation went with no problems, otherwise keep the previous
            if not chain.empty:
                calls, puts = get_calls_and_puts(chain)
                console.print("Greeks calculated by OpenBB.")
        else:
            console.print("Greeks currently not supported without IV.")

    print_raw(calls, puts, "Option chain", calls_only, puts_only, export=export)

    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "chain", chain, sheet_name
    )
