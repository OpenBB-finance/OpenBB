"""ETS Prediction View"""
__docformat__ = "numpy"

import datetime
import logging
import os
import warnings
from typing import Union

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.common.prediction_techniques import ets_model
from gamestonk_terminal.common.prediction_techniques.pred_helper import (
    price_prediction_backtesting_color,
    print_prediction_kpis,
    print_pretty_prediction,
)
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import (
    export_data,
    get_next_stock_market_days,
    patch_pandas_text_adjustment,
    plot_autoscale,
)
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)

register_matplotlib_converters()

warnings.filterwarnings("ignore")
# pylint:disable=too-many-arguments


@log_start_end(log=logger)
def display_exponential_smoothing(
    ticker: str,
    values: Union[pd.DataFrame, pd.Series],
    n_predict: int,
    trend: str = "N",
    seasonal: str = "N",
    seasonal_periods: int = 5,
    s_end_date: str = "",
    export: str = "",
    time_res: str = "",
):
    """Perform exponential smoothing

    Parameters
    ----------
    ticker : str
        Dataset being smoothed
    values : Union[pd.DataFrame, pd.Series]
        Raw data
    n_predict : int
        Days to predict
    trend : str, optional
        Trend variable, by default "N"
    seasonal : str, optional
        Seasonal variable, by default "N"
    seasonal_periods : int, optional
        Number of seasonal periods, by default 5
    s_end_date : str, optional
        End date for backtesting, by default ""
    export : str, optional
        Format to export data, by default ""
    time_res : str
        Resolution for data, allowing for predicting outside of standard market days
    """
    if s_end_date:
        if not time_res:
            future_index = get_next_stock_market_days(
                last_stock_day=s_end_date, n_next_days=n_predict
            )
        else:
            future_index = pd.date_range(
                s_end_date, periods=n_predict + 1, freq=time_res
            )[1:]

        if future_index[-1] > datetime.datetime.now():
            console.print(
                "Backtesting not allowed, since End Date + Prediction days is in the future\n"
            )
            return

        df_future = values[future_index[0] : future_index[-1]]
        values = values[:s_end_date]  # type: ignore

    # Get ETS model
    model, title, forecast = ets_model.get_exponential_smoothing_model(
        values, trend, seasonal, seasonal_periods, n_predict
    )

    if not forecast:
        console.print("No forecast made.  Model did not converge.\n")
        return

    if np.isnan(forecast).any():
        console.print("Model predicted NaN values.  Runtime Error.\n")
        return

    if not time_res:
        l_pred_days = get_next_stock_market_days(
            last_stock_day=values.index[-1],
            n_next_days=n_predict,
        )
    else:
        l_pred_days = pd.date_range(
            values.index[-1], periods=n_predict + 1, freq=time_res
        )[1:]

    df_pred = pd.Series(forecast, index=l_pred_days, name="Price")

    console.print(f"\n{title}")
    console.print("\nFit model parameters:")
    for key, value in model.params.items():
        console.print(f"{key} {' '*(18-len(key))}: {value}")

    console.print("\nAssess fit model:")
    console.print(f"AIC: {round(model.aic, 2)}")
    console.print(f"BIC: {round(model.bic, 2)}")
    console.print(f"SSE: {round(model.sse, 2)}\n")

    # Plotting
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax.plot(values.index, values.values, lw=2)
    # BACKTESTING
    if s_end_date:
        ax.set_title(f"BACKTESTING: {title} on {ticker}")
    else:
        ax.set_title(f"{title} on {ticker}")

    ax.set_xlim(
        values.index[0],
        get_next_stock_market_days(df_pred.index[-1], 1)[-1],
    )
    ax.set_xlabel("Time")
    ax.set_ylabel("Share Price ($)")
    ax.grid(b=True, which="major", color="#666666", linestyle="-")
    ax.minorticks_on()
    ax.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
    ax.plot(
        [values.index[-1], df_pred.index[0]],
        [values.values[-1], df_pred.values[0]],
        lw=1,
        c="tab:green",
        linestyle="--",
    )
    ax.plot(df_pred.index, df_pred, lw=2, c="tab:green")
    ax.axvspan(
        values.index[-1],
        df_pred.index[-1],
        facecolor="tab:orange",
        alpha=0.2,
    )
    _, _, ymin, ymax = plt.axis()
    ax.vlines(
        values.index[-1],
        ymin,
        ymax,
        linewidth=1,
        linestyle="--",
        color="k",
    )
    dateFmt = mdates.DateFormatter("%m/%d/%Y")
    ax.xaxis.set_major_formatter(dateFmt)
    ax.tick_params(axis="x", labelrotation=45)

    # BACKTESTING
    if s_end_date:
        ax.plot(
            df_future.index,
            df_future,
            lw=2,
            c="tab:blue",
            ls="--",
        )
        ax.plot(
            [values.index[-1], df_future.index[0]],
            [
                values.values[-1],
                df_future.values[0],
            ],
            lw=1,
            c="tab:blue",
            linestyle="--",
        )

    if gtff.USE_ION:
        plt.ion()

    fig.tight_layout()
    plt.show()

    # BACKTESTING
    if s_end_date:
        dateFmt = mdates.DateFormatter("%m-%d")
        fig, ax = plt.subplots(1, 2, figsize=plot_autoscale(), dpi=PLOT_DPI)
        ax0 = ax[0]
        ax0.plot(
            df_future.index,
            df_future,
            lw=2,
            c="tab:blue",
            ls="--",
        )
        ax0.plot(df_pred.index, df_pred, lw=2, c="green")
        ax0.scatter(
            df_future.index,
            df_future,
            c="tab:blue",
            lw=3,
        )
        ax0.plot(
            [values.index[-1], df_future.index[0]],
            [
                values.values[-1],
                df_future.values[0],
            ],
            lw=2,
            c="tab:blue",
            ls="--",
        )
        ax0.scatter(df_pred.index, df_pred, c="green", lw=3)
        ax0.plot(
            [values.index[-1], df_pred.index[0]],
            [values.values[-1], df_pred.values[0]],
            lw=2,
            c="green",
            ls="--",
        )
        ax0.set_title("BACKTESTING: Prices")
        ax0.set_xlim(
            values.index[-1],
            df_pred.index[-1] + datetime.timedelta(days=1),
        )
        ax0.set_ylabel("Share Price ($)")
        ax0.grid(b=True, which="major", color="#666666", linestyle="-")
        ax0.legend(["Real data", "Prediction data"])

        ax1 = ax[1]
        ax1.axhline(y=0, color="k", linestyle="--", linewidth=2)
        ax1.plot(
            df_future.index,
            100 * (df_pred.values - df_future.values) / df_future.values,
            lw=2,
            c="red",
        )
        ax1.scatter(
            df_future.index,
            100 * (df_pred.values - df_future.values) / df_future.values,
            c="red",
            lw=5,
        )
        ax1.set_title("BACKTESTING: % Error")
        ax1.plot(
            [values.index[-1], df_future.index[0]],
            [
                0,
                100 * (df_pred.values[0] - df_future.values[0]) / df_future.values[0],
            ],
            lw=2,
            ls="--",
            c="red",
        )
        ax1.set_xlim(
            values.index[-1],
            df_pred.index[-1] + datetime.timedelta(days=1),
        )
        ax1.set_xlabel("Time")
        ax1.set_ylabel("Prediction Error (%)")
        ax1.grid(b=True, which="major", color="#666666", linestyle="-")
        ax1.legend(["Real data", "Prediction data"])

        ax0.xaxis.set_major_formatter(dateFmt)
        ax0.tick_params(axis="x", labelrotation=45)
        ax1.xaxis.set_major_formatter(dateFmt)
        ax1.tick_params(axis="x", labelrotation=45)

        if gtff.USE_ION:
            plt.ion()
        fig.tight_layout()
        plt.show()

        # Refactor prediction dataframe for backtesting print
        df_pred.name = "Prediction"
        df_pred = df_pred.to_frame()
        df_pred["Real"] = df_future

        if gtff.USE_COLOR:

            patch_pandas_text_adjustment()

            console.print("Time         Real [$]  x  Prediction [$]")
            console.print(
                df_pred.apply(price_prediction_backtesting_color, axis=1).to_string()
            )
        else:
            console.print(df_pred[["Real", "Prediction"]].round(2).to_string())

        console.print("")
        print_prediction_kpis(df_pred["Real"].values, df_pred["Prediction"].values)

    else:
        # Print prediction data
        print_pretty_prediction(df_pred, values.values[-1])
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "ets")

    console.print("")
