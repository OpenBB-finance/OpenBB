""" Regression View"""
__docformat__ = "numpy"

import logging
import os
from typing import Union, Optional, List

import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters

from openbb_terminal.common.prediction_techniques import regression_model
from openbb_terminal.common.prediction_techniques.pred_helper import (
    lambda_price_prediction_backtesting_color,
    print_prediction_kpis,
    print_pretty_prediction,
)
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    get_next_stock_market_days,
    patch_pandas_text_adjustment,
    plot_autoscale,
)
from openbb_terminal.rich_config import console
from openbb_terminal import rich_config

logger = logging.getLogger(__name__)

register_matplotlib_converters()

# pylint:disable=too-many-arguments


@log_start_end(log=logger)
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
    external_axes: Optional[List[plt.Axes]] = None,
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
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
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

        df_future = values[future_index[0] : future_index[-1]]  # noqa: E203
        values = values[:s_end_date]  # type: ignore

    l_predictions, _ = regression_model.get_regression_model(
        list(values.values), poly_order, n_input, n_predict, n_jumps
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

    # This plot has 1 axes
    if external_axes is None:
        _, ax1 = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if (not s_end_date and len(external_axes) != 1) or (
            s_end_date and len(external_axes) != 3
        ):
            logger.error("Expected list of 1 axis or 3 axes when backtesting.")
            console.print(
                "[red]Expected list of 1 axis or 3 axes when backtesting./n[/red]"
            )
            return
        ax1 = external_axes[0]

    ax1.plot(values.index, values)
    # BACKTESTING
    if s_end_date:
        ax1.set_title(
            f"BACKTESTING: Regression (polynomial {poly_order}) on {dataset} - {n_predict} step prediction",
            fontsize=12,
        )
    else:
        ax1.set_title(
            f"Regression (polynomial {poly_order}) on {dataset} - {n_predict} step prediction"
        )
    ax1.set_xlim(values.index[0], l_pred_days[-1])
    ax1.set_ylabel("Value")
    ax1.plot(
        [values.index[-1], df_pred.index[0]],
        [values.values[-1], df_pred.values[0]],
        color=theme.down_color,
        linestyle="--",
    )
    ax1.plot(df_pred.index, df_pred, color=theme.down_color)
    ax1.axvspan(values.index[-1], df_pred.index[-1], alpha=0.2)
    _, _, ymin, ymax = plt.axis()
    ax1.vlines(values.index[-1], ymin, ymax, linestyle="--")

    # BACKTESTING
    if s_end_date:
        ax1.plot(
            df_future.index,
            df_future,
            color=theme.up_color,
            linestyle="--",
        )
        ax1.plot(
            [values.index[-1], df_future.index[0]],
            [
                values.values[-1],
                df_future.values[0],
            ],
            color=theme.up_color,
            linestyle="--",
        )

    theme.style_primary_axis(ax1)

    if external_axes is None:
        theme.visualize_output()

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "regression")
    console.print("")

    # BACKTESTING
    if s_end_date:
        # This plot has 1 axes
        if external_axes is None:
            _, axes = plt.subplots(
                2, 1, sharex=True, figsize=plot_autoscale(), dpi=PLOT_DPI
            )
            (ax2, ax3) = axes
        else:
            if len(external_axes) != 3:
                logger.error("Expected list of three axis items.")
                console.print("[red]Expected list of 3 axis items./n[/red]")
                return
            (_, ax2, ax3) = external_axes

        ax2.plot(
            df_future.index,
            df_future,
            color=theme.up_color,
            linestyle="--",
        )
        ax2.plot(df_pred.index, df_pred, color=theme.down_color, marker="o")
        ax2.plot(
            [values.index[-1], df_future.index[0]],
            [
                values.values[-1],
                df_future.values[0],
            ],
            color=theme.up_color,
            linestyle="--",
        )
        ax2.plot(
            [values.index[-1], df_pred.index[0]],
            [values.values[-1], df_pred.values[0]],
            color=theme.down_color,
            linestyle="--",
            marker="o",
        )
        ax2.set_title("BACKTESTING: Real data vs Prediction", fontsize=12)
        ax2.set_xlim(values.index[-1], df_pred.index[-1])
        ax2.set_ylabel("Value")
        ax2.legend(["Real data", "Prediction data"])

        ax3.axhline(y=0, linestyle="--", color=theme.up_color)
        ax3.plot(
            df_future.index,
            100 * (df_pred.values - df_future.values) / df_future.values,
            color=theme.down_color,
            marker="o",
        )
        ax3.set_title(
            "BACKTESTING: Error between Real data and Prediction [%]", fontsize=12
        )
        ax3.plot(
            [values.index[-1], df_future.index[0]],
            [
                0,
                100 * (df_pred.values[0] - df_future.values[0]) / df_future.values[0],
            ],
            linestyle="--",
            color=theme.down_color,
        )
        ax3.set_xlim(values.index[-1], df_pred.index[-1])
        ax3.set_xlabel("Time")
        ax3.set_ylabel("Error (%)")
        ax3.legend(["Real data", "Prediction data"])

        theme.style_primary_axis(ax2)
        theme.style_primary_axis(ax3)

        if external_axes is None:
            theme.visualize_output()

        # Refactor prediction dataframe for backtesting print
        df_pred.name = "Prediction"
        df_pred = df_pred.to_frame()
        df_pred["Real"] = df_future

        if rich_config.USE_COLOR:

            patch_pandas_text_adjustment()

            console.print("Time         Real [$]  x  Prediction [$]")
            console.print(
                df_pred.apply(
                    lambda_price_prediction_backtesting_color, axis=1
                ).to_string()
            )
        else:
            console.print(df_pred[["Real", "Prediction"]].round(2).to_string())

        console.print("")
        print_prediction_kpis(df_pred["Real"].values, df_pred["Prediction"].values)

    else:
        # Print prediction data
        print_pretty_prediction(df_pred, values.values[-1])
    console.print("")
