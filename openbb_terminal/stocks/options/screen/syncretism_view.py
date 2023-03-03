"""Syncretistm View module"""
__docformat__ = "numpy"

import configparser
import logging
import os
from typing import List, Optional, Union

from openbb_terminal import OpenBBFigure
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.options.screen import syncretism_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def view_available_presets(preset: str):
    """View available presets.

    Parameters
    ----------
    preset: str
        Chosen preset
    """
    if preset:
        preset_filter = configparser.RawConfigParser()
        preset_filter.optionxform = str  # type: ignore
        preset_choices = syncretism_model.get_preset_choices()
        preset_filter.read(preset_choices[preset])
        filters_headers = ["FILTER"]

        for i, filter_header in enumerate(filters_headers):
            console.print(f" - {filter_header} -")
            d_filters = {**preset_filter[filter_header]}
            d_filters = {k: v for k, v in d_filters.items() if v}

            if d_filters:
                max_len = len(max(d_filters, key=len)) + 2
                for key, value in d_filters.items():
                    console.print(f"{key}{(max_len-len(key))*' '}: {value}")

            if i < len(filters_headers) - 1:
                console.print("\n")

    else:
        console.print("Please provide a preset template.")


@log_start_end(log=logger)
def view_screener_output(
    preset: str,
    limit: int = 25,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> List:
    """Print the output of screener

    Parameters
    ----------
    preset: str
        Chosen preset
    limit: int
        Number of randomly sorted rows to display
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format for export file

    Returns
    -------
    List
        List of tickers screened
    """
    df_res, error_msg = syncretism_model.get_screener_output(preset)
    if error_msg:
        console.print(error_msg, "\n")
        return []

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "scr",
        df_res,
        sheet_name,
    )

    if limit > 0:
        df_res = df_res.head(limit)

    print_rich_table(
        df_res,
        headers=df_res.columns.tolist(),
        show_index=False,
        title="Screener Output",
        floatfmt=".4f",
        export=bool(export),
    )

    return list(set(df_res["Ticker"].values))


# pylint:disable=too-many-arguments


@log_start_end(log=logger)
def view_historical_greeks(
    symbol: str,
    expiry: str,
    strike: Union[float, str],
    greek: str = "Delta",
    chain_id: str = "",
    put: bool = False,
    raw: bool = False,
    limit: Union[int, str] = 20,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
):
    """Plots historical greeks for a given option. [Source: Syncretism]

    Parameters
    ----------
    symbol: str
        Stock ticker
    expiry: str
        Expiration date
    strike: Union[str, float]
        Strike price to consider
    greek: str
        Greek variable to plot
    chain_id: str
        OCC option chain.  Overwrites other variables
    put: bool
        Is this a put option?
    raw: bool
        Print to console
    limit: int
        Number of rows to show in raw
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df = syncretism_model.get_historical_greeks(symbol, expiry, strike, chain_id, put)
    if df is None or df.empty:
        return None

    if isinstance(limit, str):
        try:
            limit = int(limit)
        except ValueError:
            return console.print(
                f"[red]Could not convert limit of {limit} to a number.[/red]\n"
            )

    if raw:
        print_rich_table(
            df.tail(limit),
            headers=df.columns.tolist(),
            title="Historical Greeks",
            show_index=True,
            floatfmt=".4f",
            export=bool(export),
        )

    fig = OpenBBFigure.create_subplots(
        specs=[[{"secondary_y": True}]],
        vertical_spacing=0.06,
    )
    fig.set_title(
        f"{(greek).capitalize()} historical for {symbol.upper()} {strike} {['Call','Put'][put]}"
    )
    fig.add_scatter(
        x=df.index,
        y=df.price,
        name="Stock Price",
        line=dict(color=theme.down_color),
    )
    fig.add_scatter(
        x=df.index,
        y=df[greek.lower()],
        name=greek.title(),
        line=dict(color=theme.up_color),
        yaxis="y2",
    )
    fig.update_layout(
        margin=dict(t=30),
        yaxis2=dict(
            side="left",
            title=greek,
            overlaying="y",
        ),
        yaxis=dict(
            title=f"{symbol} Price",
        ),
    )
    fig.hide_holidays()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "grhist",
        df,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)
