""" Regression View"""
__docformat__ = "numpy"

from typing import Union
import os
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters

from gamestonk_terminal.helper_funcs import (
    patch_pandas_text_adjustment,
    get_next_stock_market_days,
    plot_autoscale,
    export_data,
)

from gamestonk_terminal.common.prediction_techniques.pred_helper import (
    print_pretty_prediction,
    price_prediction_backtesting_color,
    print_prediction_kpis,
)

from gamestonk_terminal.common.prediction_techniques import regression_model
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.rich_config import console

register_matplotlib_converters()

# pylint:disable=too-many-arguments


def display_regression(
    dataset: str,
    values: Union[pd.Series, pd.DataFrame],
    poly_order: int,
    n_input: int,
    n_predict: int,
    n_jumps: int,
    s_end_date: str = "",
    export: str = "",
    time_res: str = "",
):
    """Display predications for regression models

    Parameters
    ----------
    dataset : str
        Title for data
    values : Union[pd.Series, pd.DataFrame]
        Data to fit
    poly_order : int
        Order of polynomial to fit
    n_input : int
        Length of input sequence
    n_predict : int
        Length of prediction sequence
    n_jumps : int
        Number of jumps in data
    s_end_date : str, optional
        Start date for backtesting
    export : str, optional
        Format for exporting figures
    time_res : str
        Resolution for data, allowing for predicting outside of standard market days
    """
    # BACKTESTING
    if s_end_date:
        if not time_res:
            future_index = get_next_stock_market_days(
                last_stock_day=s_end_date, n_next_days=n_predict
            )
        else:
            future_index = pd.date_range(
                s_end_date, periods=n_predict + 1, freq=time_res
            )[1:]

        df_future = values[future_index[0] : future_index[-1]]
        values = values[:s_end_date]  # type: ignore

    l_predictions, _ = regression_model.get_regression_model(
        values, poly_order, n_input, n_predict, n_jumps
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

    # Plotting
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax.plot(values.index, values, lw=2)
    # BACKTESTING
    if s_end_date:
        ax.set_title(
            f"BACKTESTING: Regression (polynomial {poly_order}) on {dataset} - {n_predict} step prediction"
        )
    else:
        ax.set_title(
            f"Regression (polynomial {poly_order}) on {dataset} - {n_predict} step prediction"
        )
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
    fig.tight_layout()
    if gtff.USE_ION:
        plt.ion()

    plt.show()

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "regression")
    console.print("")

    # BACKTESTING
    if s_end_date:
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
        ax0.set_title("BACKTESTING: Real data vs Prediction")
        ax0.set_xlim(values.index[-1], df_pred.index[-1])
        ax0.set_xticks([values.index[-1], df_pred.index[-1]])
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
        ax1.set_xlim(values.index[-1], df_pred.index[-1])
        ax1.set_xticks([values.index[-1], df_pred.index[-1]])
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
    console.print("")
