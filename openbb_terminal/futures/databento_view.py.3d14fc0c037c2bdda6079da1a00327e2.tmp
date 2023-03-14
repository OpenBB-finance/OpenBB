"""DataBento view"""
__docformat__ = "numpy"

import os
from typing import List, Optional

import mplfinance as mpf
from matplotlib import pyplot as plt

from openbb_terminal.config_terminal import theme
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    lambda_long_number_format_y_axis,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.rich_config import console
from openbb_terminal.stocks import databento_model


def display_historical(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display historical futures [Source: DataBento]

    Parameters
    ----------
    symbol: List[str]
        Symbol to display
    start_date: Optional[str]
        Start date of the historical data with format YYYY-MM-DD
    end_date: Optional[str]
        End date of the historical data with format YYYY-MM-DD
    raw: bool
        Display futures timeseries in raw format
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Type of format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    data = databento_model.get_historical_futures(
        symbol.upper(), start_date=start_date, end_date=end_date
    )
    if data.empty:
        console.print(f"No data found for {symbol}.")
        return
    # We check if there's Volume data to avoid errors and empty subplots
    has_volume = False
    if "Volume" in data.columns:
        has_volume = bool(data["Volume"].sum() > 0)

    candle_chart_kwargs = {
        "type": "candle",
        "style": theme.mpf_style,
        "volume": has_volume,
        "addplot": [],
        "xrotation": theme.xticks_rotation,
        "scale_padding": {"left": 0.3, "right": 1, "top": 0.8, "bottom": 0.8},
        "update_width_config": {
            "candle_linewidth": 0.6,
            "candle_width": 0.8,
            "volume_linewidth": 0.8,
            "volume_width": 0.8,
        },
        "warn_too_much_data": 10000,
    }
    if external_axes is None:
        candle_chart_kwargs["returnfig"] = True
        candle_chart_kwargs["figratio"] = (10, 7)
        candle_chart_kwargs["figscale"] = 1.10
        candle_chart_kwargs["figsize"] = plot_autoscale()
        candle_chart_kwargs["warn_too_much_data"] = 100_000

        fig, ax = mpf.plot(data, **candle_chart_kwargs)

        if has_volume:
            lambda_long_number_format_y_axis(data, "Volume", ax)

        fig.suptitle(
            f"{symbol}",
            x=0.055,
            y=0.965,
            horizontalalignment="left",
        )
        theme.visualize_output(force_tight_layout=False)
    elif (has_volume and is_valid_axes_count(external_axes, 2)) or (
        not has_volume and is_valid_axes_count(external_axes, 1)
    ):
        candle_chart_kwargs["ax"] = external_axes[0]
        if has_volume:
            candle_chart_kwargs["volume"] = external_axes[1]
        mpf.plot(data, **candle_chart_kwargs)

    if raw:
        print_rich_table(
            data,
            headers=list(data.columns),
            show_index=True,
            title="Futures timeseries",
        )
        console.print()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "historical_db",
        data,
        sheet_name,
    )
