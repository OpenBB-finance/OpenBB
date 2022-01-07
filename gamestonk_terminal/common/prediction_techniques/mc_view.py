"""Monte Carlo View"""
__docformat__ = "numpy"

from typing import Union
import os

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from gamestonk_terminal.common.prediction_techniques import mc_model
from gamestonk_terminal.helper_funcs import (
    plot_autoscale,
    get_next_stock_market_days,
    export_data,
)
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff


def display_mc_forecast(
    data: Union[pd.Series, np.ndarray],
    n_future: int,
    n_sims: int,
    use_log=True,
    fig_title: str = "",
    export: str = "",
    time_res: str = "",
):
    """Display monte carlo forecasting

    Parameters
    ----------
    data : Union[pd.Series, np.array]
        Data to forecast
    n_future : int
        Number of days to forecast
    n_sims : int
        Number of simulations to run
    use_log : bool, optional
        Flag to use lognormal, by default True
    fig_title : str
        Figure title
    export: str
        Format to export data
    time_res : str
        Resolution for data, allowing for predicting outside of standard market days
    """
    predicted_values = mc_model.get_mc_brownian(data, n_future, n_sims, use_log)
    if not time_res or time_res == "1D":
        future_index = get_next_stock_market_days(data.index[-1], n_next_days=n_future)  # type: ignore
    else:
        future_index = pd.date_range(data.index[-1], periods=n_future + 1, freq=time_res)[1:]  # type: ignore

    dateFmt = mdates.DateFormatter("%m/%d/%Y")

    fig, ax = plt.subplots(1, 2, figsize=plot_autoscale(), dpi=PLOT_DPI)

    ax[0].plot(data)
    ax[0].plot(future_index, predicted_values, alpha=0.3)
    ax[0].set_title("Data Predictions")
    ax[0].xaxis.set_major_formatter(dateFmt)
    ax[0].tick_params(axis="x", labelrotation=45)
    ax[0].grid("on")

    sns.histplot(predicted_values[-1, :], ax=ax[1], kde=True)
    ax[1].set_xlabel("Final Value")
    ax[1].axvline(x=data.values[-1], c="k", label="Last Value", lw=3, ls="-")  # type: ignore
    ax[1].set_title(f"Distribution of final values after {n_future} steps.")
    ax[1].set_xlim(np.min(predicted_values[-1, :]), np.max(predicted_values[-1, :]))
    ax[1].grid("on")
    ax[1].legend()
    if fig_title:
        fig.suptitle(fig_title)
    fig.tight_layout(pad=2)

    if gtff.USE_ION:
        plt.ion()
    plt.show()
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "mc")
    print("")
