import logging
import os
from datetime import datetime
from typing import Optional

import numpy as np
import pandas as pd

from openbb_terminal import OpenBBFigure, theme
from openbb_terminal.cryptocurrency.overview.glassnode_model import get_btc_rainbow
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import export_data

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_GLASSNODE_KEY"])
def display_btc_rainbow(
    start_date: str = "2010-01-01",
    end_date: Optional[str] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
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
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    df_data = get_btc_rainbow(start_date, end_date)

    if df_data.empty:
        return None

    fig = OpenBBFigure(yaxis_title="Price [USD]")
    fig.set_title("Bitcoin Rainbow Chart")

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

    color_list = [
        "rgba(255, 0, 0, 0.7)",
        "rgba(255, 165, 0, 0.7)",
        "rgba(255, 255, 0, 0.7)",
        "rgba(0, 128, 0, 0.7)",
        "rgba(0, 0, 255, 0.7)",
        "rgba(238, 130, 238, 0.7)",
        "rgba(75, 0, 130, 0.7)",
        "rgba(128, 0, 128, 0.7)",
    ]
    labels = [
        "Bubble bursting imminent!!",
        "SELL!",
        "Everyone FOMO'ing....",
        "Is this a bubble??",
        "Still cheap",
        "Accumulate",
        "BUY!",
        "Basically a Fire Sale",
        "Bitcoin Price",
    ]
    for i, (ytop, ybottom, color, label) in enumerate(
        zip(
            [y1, y2, y3, y4, y5, y6, y7, y8],
            [y0, y1, y2, y3, y4, y5, y6, y7],
            color_list,
            labels,
        )
    ):
        fig.add_scatter(
            x=x_dates,
            y=ytop,
            mode="lines",
            line_color=color,
            showlegend=False,
            name="",
        )
        fig.add_scatter(
            x=x_dates,
            y=ybottom,
            mode="lines",
            fill="tonexty",
            fillcolor=color,
            line_color=color,
            name=label,
        )

    fig.add_scatter(
        x=df_data.index,
        y=df_data["v"].values,
        mode="lines",
        line_color=theme.get_colors()[0],
        name="Bitcoin Price",
    )

    sample_dates = [
        datetime(2012, 11, 28),
        datetime(2016, 7, 9),
        datetime(2020, 5, 11),
        datetime(2024, 4, 4),
    ]

    for i, date in enumerate(sample_dates):
        if d0 < date < dend:
            fig.add_vline(x=date, line_width=2, line_color="grey")
            fig.add_annotation(
                x=date,
                y=min(y0),
                text=f"Halving {i+1}",
                textangle=90,
                xshift=10,
                yshift=-120,
                font=dict(color="grey"),
            )

    fig.update_layout(legend=dict(traceorder="normal"), yaxis_type="log")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "btcrb",
        df_data,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)
