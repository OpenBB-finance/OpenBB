import logging
import os
from datetime import datetime
from typing import List, Optional

import matplotlib
import numpy as np
import pandas as pd
from matplotlib import (
    dates as mdates,
    pyplot as plt,
)

from openbb_terminal import config_plot as cfgPlot
from openbb_terminal.config_terminal import theme
from openbb_terminal.cryptocurrency.overview.glassnode_model import get_btc_rainbow
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    plot_autoscale,
)

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_GLASSNODE_KEY"])
def display_btc_rainbow(
    start_date: str = "2010-01-01",
    end_date: Optional[str] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Displays bitcoin rainbow chart
    [Price data from source: https://glassnode.com]
    [Inspired by: https://blockchaincenter.net]

    Parameters
    ----------
    start_date : str
        Initial date, format YYYY-MM-DD
    end_date : Optional[str]
        Final date, format YYYY-MM-DD
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    df_data = get_btc_rainbow(start_date, end_date)

    if df_data.empty:
        return

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    d0 = datetime.strptime("2012-01-01", "%Y-%m-%d")
    dend = datetime.strptime(end_date, "%Y-%m-%d")

    x = range((df_data.index[0] - d0).days, (dend - d0).days + 1)

    y0 = [10 ** ((2.90 * ln_x) - 19.463) for ln_x in [np.log(val + 1400) for val in x]]
    y1 = [10 ** ((2.886 * ln_x) - 19.463) for ln_x in [np.log(val + 1375) for val in x]]
    y2 = [10 ** ((2.872 * ln_x) - 19.463) for ln_x in [np.log(val + 1350) for val in x]]
    y3 = [10 ** ((2.859 * ln_x) - 19.463) for ln_x in [np.log(val + 1320) for val in x]]
    y4 = [
        10 ** ((2.8445 * ln_x) - 19.463) for ln_x in [np.log(val + 1293) for val in x]
    ]
    y5 = [
        10 ** ((2.8295 * ln_x) - 19.463) for ln_x in [np.log(val + 1275) for val in x]
    ]
    y6 = [10 ** ((2.815 * ln_x) - 19.463) for ln_x in [np.log(val + 1250) for val in x]]
    y7 = [10 ** ((2.801 * ln_x) - 19.463) for ln_x in [np.log(val + 1225) for val in x]]
    y8 = [10 ** ((2.788 * ln_x) - 19.463) for ln_x in [np.log(val + 1200) for val in x]]

    x_dates = pd.date_range(df_data.index[0], dend, freq="d")

    ax.fill_between(x_dates, y0, y1, color="red", alpha=0.7)
    ax.fill_between(x_dates, y1, y2, color="orange", alpha=0.7)
    ax.fill_between(x_dates, y2, y3, color="yellow", alpha=0.7)
    ax.fill_between(x_dates, y3, y4, color="green", alpha=0.7)
    ax.fill_between(x_dates, y4, y5, color="blue", alpha=0.7)
    ax.fill_between(x_dates, y5, y6, color="violet", alpha=0.7)
    ax.fill_between(x_dates, y6, y7, color="indigo", alpha=0.7)
    ax.fill_between(x_dates, y7, y8, color="purple", alpha=0.7)

    ax.semilogy(df_data.index, df_data["v"].values)
    ax.set_xlim(df_data.index[0], dend)
    ax.set_title("Bitcoin Rainbow Chart")
    ax.set_ylabel("Price [USD]")

    ax.legend(
        [
            "Bubble bursting imminent!!",
            "SELL!",
            "Everyone FOMO'ing....",
            "Is this a bubble??",
            "Still cheap",
            "Accumulate",
            "BUY!",
            "Basically a Fire Sale",
            "Bitcoin Price",
        ],
        prop={"size": 8},
    )

    sample_dates = np.array(
        [
            datetime(2012, 11, 28),
            datetime(2016, 7, 9),
            datetime(2020, 5, 11),
            datetime(2024, 4, 4),
        ]
    )
    sample_dates = mdates.date2num(sample_dates)
    ax.vlines(x=sample_dates, ymin=0, ymax=max(y0), color="grey")
    for i, x in enumerate(sample_dates):
        if mdates.date2num(d0) < x < mdates.date2num(dend):
            ax.text(x, 1, f"Halving {i+1}", rotation=-90, verticalalignment="center")

    ax.minorticks_off()
    ax.yaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, _: int(x) if x >= 1 else x)
    )
    ax.yaxis.set_major_locator(
        matplotlib.ticker.LogLocator(base=100, subs=[1.0, 2.0, 5.0, 10.0])
    )

    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "btcrb",
        df_data,
        sheet_name,
    )
