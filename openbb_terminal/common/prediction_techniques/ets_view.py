"""ETS Prediction View"""
__docformat__ = "numpy"

import datetime
import logging
import os
import warnings
from typing import Union, Optional, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from openbb_terminal.config_terminal import theme
from openbb_terminal.common.prediction_techniques import ets_model
from openbb_terminal.common.prediction_techniques.pred_helper import (
    lambda_price_prediction_backtesting_color,
    print_prediction_kpis,
    print_pretty_prediction,
)
from openbb_terminal.config_plot import PLOT_DPI
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
    external_axes: Optional[List[plt.Axes]] = None,
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
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
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
                "Backtesting not allowed,"
                + " since End Date + Prediction days is in the future\n"
            )
            return

        df_future = values[future_index[0] : future_index[-1]]  # noqa: E203
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

    # This plot has 1 axes
    if external_axes is None:
        _, ax1 = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if (not s_end_date and len(external_axes) != 1) or (
            s_end_date and len(external_axes) != 3
        ):
            logger.error(
                "Expected list of 1 axis item or 3 axis items when backtesting"
            )
            console.print(
                "[red]Expected list of 1 axis item "
                + "or 3 axis items when backtesting.\n[/red]"
            )
            return
        ax1 = external_axes[0]

    ax1.plot(values.index, values.values)

    # BACKTESTING
    if s_end_date:
        ax1.set_title(f"BACKTESTING: {title} on {ticker}", fontsize=12)
    else:
        ax1.set_title(f"{title} on {ticker}", fontsize=12)

    ax1.set_xlim(
        values.index[0],
        get_next_stock_market_days(df_pred.index[-1], 1)[-1],
    )
    ax1.set_ylabel("Value")
    ax1.plot(
        [values.index[-1], df_pred.index[0]],
        [values.values[-1], df_pred.values[0]],
        color=theme.down_color,
        linestyle="--",
    )
    ax1.plot(df_pred.index, df_pred, color=theme.down_color)
    ax1.axvspan(
        values.index[-1],
        df_pred.index[-1],
        facecolor=theme.down_color,
        alpha=0.2,
    )
    _, _, ymin, ymax = plt.axis()
    ax1.vlines(
        values.index[-1],
        ymin,
        ymax,
        linestyle="--",
        color=theme.get_colors(reverse=True)[0],
    )

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
                console.print("[red]Expected list of 1 axis item.\n[/red]")
                return
            (_, ax2, ax3) = external_axes

        ax2.plot(
            df_future.index,
            df_future,
            color=theme.up_color,
            linestyle="--",
        )
        ax2.plot(df_pred.index, df_pred)
        ax2.scatter(
            df_future.index,
            df_future,
            color=theme.up_color,
        )
        ax2.plot(
            [values.index[-1], df_future.index[0]],
            [
                values.values[-1],
                df_future.values[0],
            ],
            color=theme.up_color,
            linestyle="--",
        )
        ax2.scatter(df_pred.index, df_pred)
        ax2.plot(
            [values.index[-1], df_pred.index[0]],
            [values.values[-1], df_pred.values[0]],
            linestyle="--",
        )
        ax2.set_title("BACKTESTING: Values")
        ax2.set_xlim(
            values.index[-1],
            df_pred.index[-1] + datetime.timedelta(days=1),
        )
        ax2.set_ylabel("Value")
        ax2.legend(["Real data", "Prediction data"])
        theme.style_primary_axis(ax2)

        ax3.axhline(y=0, linestyle="--")
        ax3.plot(
            df_future.index,
            100 * (df_pred.values - df_future.values) / df_future.values,
            color=theme.down_color,
        )
        ax3.scatter(
            df_future.index,
            100 * (df_pred.values - df_future.values) / df_future.values,
            color=theme.down_color,
        )
        ax3.set_title("BACKTESTING: % Error")
        ax3.plot(
            [values.index[-1], df_future.index[0]],
            [
                0,
                100 * (df_pred.values[0] - df_future.values[0]) / df_future.values[0],
            ],
            ls="--",
            color=theme.down_color,
        )
        ax3.set_xlim(
            values.index[-1],
            df_pred.index[-1] + datetime.timedelta(days=1),
        )
        ax3.set_ylabel("Prediction Error (%)")
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
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "ets")
