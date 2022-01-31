""" ARIMA Prediction View """
__docformat__ = "numpy"


import datetime
import logging
import os
from typing import Union

import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.common.prediction_techniques import arima_model
from gamestonk_terminal.common.prediction_techniques.pred_helper import (
    print_prediction_kpis,
    print_pretty_prediction,
)
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import (
    export_data,
    get_next_stock_market_days,
    plot_autoscale,
    print_rich_table,
)
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)

register_matplotlib_converters()

# pylint:disable=too-many-arguments


@log_start_end(log=logger)
def display_arima(
    dataset: str,
    values: Union[pd.DataFrame, pd.Series],
    arima_order: str,
    n_predict: int,
    seasonal: bool,
    ic: str,
    results: bool,
    s_end_date: str = "",
    export: str = "",
    time_res: str = "",
):
    """View fit ARIMA model

    Parameters
    ----------
    dataset : str
        String indicating dataset (for plot title)
    values : Union[pd.DataFrame, pd.Series]
        Data to fit
    arima_order : str
        String of ARIMA params in form "p,q,d"
    n_predict : int
        Days to predict
    seasonal : bool
        Flag to use seasonal model
    ic : str
        Information Criteria for model evaluation
    results : bool
        Flag to display model summary
    s_end_date : str, optional
        Specified end date for backtesting comparisons
    export : str, optional
        Format to export image
    time_res : str
        Resolution for data, allowing for predicting outside of standard market days
    """

    if arima_order:
        t_order = tuple(int(ord) for ord in arima_order.split(","))
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

    l_predictions, model = arima_model.get_arima_model(
        values, arima_order, n_predict, seasonal, ic
    )

    # Prediction data
    if not time_res:
        l_pred_days = get_next_stock_market_days(
            last_stock_day=values.index[-1],
            n_next_days=n_predict,
        )
    else:
        l_pred_days = pd.date_range(
            values.index[-1], periods=n_predict + 1, freq=time_res
        )[1:]

    df_pred = pd.Series(l_predictions, index=l_pred_days, name="Price")

    if results:
        console.print(model.summary())
        console.print("")

    # Plotting
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax.plot(values.index, values, lw=2)

    # pylint:disable=no-member

    if arima_order:
        # BACKTESTING
        if s_end_date:
            ax.set_title(
                f"BACKTESTING: ARIMA {str(t_order)} on {dataset} - {n_predict} step prediction"
            )
        else:
            ax.set_title(
                f"ARIMA {str(t_order)} on {dataset} - {n_predict} step prediction"
            )
    else:
        # BACKTESTING
        if s_end_date:
            ax.set_title(
                f"BACKTESTING: ARIMA {model.order} on {dataset} - {n_predict} step prediction"
            )
        else:
            plt.title(f"ARIMA {model.order} on {dataset} - {n_predict} step prediction")
    ax.set_xlim(values.index[0], l_pred_days[-1])
    ax.set_xlabel("Time")
    ax.set_ylabel("Value")
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
    ax.axvspan(values.index[-1], df_pred.index[-1], facecolor="tab:orange", alpha=0.2)
    _, _, ymin, ymax = plt.axis()
    ax.vlines(values.index[-1], ymin, ymax, linewidth=1, linestyle="--", color="k")

    # BACKTESTING
    if s_end_date:
        ax.plot(
            df_future.index,
            df_future.values,
            lw=2,
            c="tab:blue",
            ls="--",
        )
        plt.plot(
            [values.index[-1], df_future.index[0]],
            [
                values.values[-1],
                df_future.values[0],
            ],
            lw=1,
            c="tab:blue",
            linestyle="--",
        )

    fig.tight_layout()
    if gtff.USE_ION:
        plt.ion()

    plt.show()

    # BACKTESTING
    if s_end_date:
        fig, ax = plt.subplots(1, 2, figsize=plot_autoscale(), dpi=PLOT_DPI)
        ax0 = ax[0]
        ax0.plot(
            df_future.index,
            df_future.values,
            lw=2,
            c="tab:blue",
            ls="--",
        )
        ax0.plot(df_pred.index, df_pred, lw=2, c="green")
        ax0.scatter(df_future.index, df_future, c="tab:blue", lw=3)
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
        ax0.set_title("BACKTESTING: Real data Prediction")
        ax0.set_xlim(values.index[-1], df_pred.index[-1] + datetime.timedelta(days=1))
        ax0.set_xticks(
            [values.index[-1], df_pred.index[-1] + datetime.timedelta(days=1)]
        )
        ax0.set_ylabel("Value")
        ax0.grid(b=True, which="major", color="#666666", linestyle="-")
        ax0.minorticks_on()
        ax0.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
        ax0.legend(["Real data", "Prediction data"])
        ax0.set_xticks([])

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
        ax1.set_title("BACKTESTING: Error between Real data and Prediction [%]")
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
        ax1.set_xlim(values.index[-1], df_pred.index[-1] + datetime.timedelta(days=1))
        ax1.set_xticks(
            [values.index[-1], df_pred.index[-1] + datetime.timedelta(days=1)]
        )
        ax1.set_xlabel("Time")
        ax1.set_ylabel("Prediction Error (%)")
        ax1.grid(b=True, which="major", color="#666666", linestyle="-")
        ax1.minorticks_on()
        ax1.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
        ax1.legend(["Real data", "Prediction data"])
        fig.tight_layout()
        if gtff.USE_ION:
            plt.ion()

        plt.show()

        # Refactor prediction dataframe for backtesting print
        df_pred.name = "Prediction"
        df_pred = df_pred.to_frame()
        df_pred["Real"] = df_future.values

        if gtff.USE_COLOR:
            df_pred["Real"] = df_pred["Real"].astype(float)
            df_pred["Prediction"] = df_pred["Prediction"].astype(float)
            df_pred["Dif"] = 100 * (df_pred.Prediction - df_pred.Real) / df_pred.Real
            print_rich_table(
                df_pred,
                headers=["Date", "Predicted", "Actual", "% Difference"],
                show_index=True,
                title="ARIMA Model",
            )
        else:
            df_pred["Real"] = df_pred["Real"].astype(float)
            df_pred["Prediction"] = df_pred["Predicted"].astype(float)
            df_pred["Dif"] = 100 * (df_pred.Prediction - df_pred.Real) / df_pred.Real
            print_rich_table(
                df_pred,
                headers=["Date", "Predicted", "Actual", "% Difference"],
                show_index=True,
                title="ARIMA Model",
            )

        console.print("")
        print_prediction_kpis(df_pred["Real"].values, df_pred["Prediction"].values)

    else:
        # Print prediction data
        print_pretty_prediction(df_pred, values.values[-1])
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "arima")
    console.print("")
