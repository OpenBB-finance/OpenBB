""" ARIMA Prediction View """
__docformat__ = "numpy"


import datetime
import logging
import os
from typing import Union, Optional, List

import matplotlib.pyplot as plt
import pandas as pd

from gamestonk_terminal.common.prediction_techniques import arima_model
from gamestonk_terminal.common.prediction_techniques.pred_helper import (
    print_prediction_kpis,
    print_pretty_prediction,
)
from gamestonk_terminal.config_terminal import theme
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import (
    export_data,
    get_next_stock_market_days,
    plot_autoscale,
    print_rich_table,
)
from gamestonk_terminal.rich_config import console
from gamestonk_terminal import rich_config

logger = logging.getLogger(__name__)

# pylint:disable=too-many-arguments,too-many-branches

# TODO: HELP WANTED! The logic of this view is pretty convoluted and it overlaps with
#       other views of this submenu. It would be great to refactor it in a way the
#       `pylint:disable` flag above can be removed and the backtesting related code is
#       reused by multiple views.


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
    external_axes: Optional[List[plt.Axes]] = None,
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
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
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

        df_future = values[future_index[0] : future_index[-1]]  # noqa: E203
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

    # This plot has 1 axes
    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if (not s_end_date and len(external_axes) != 1) or (
            s_end_date and len(external_axes) != 3
        ):
            logger.error(
                "Expected list of 1 axis item or 3 axis items when backtesting"
            )
            console.print(
                "[red]Expected list of 1 axis item "
                + "or 3 axis items when backtesting./n[/red]"
            )
            return
        ax = external_axes[0]

    ax.plot(values.index, values)

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
    ax.set_ylabel("Value")
    ax.plot(
        [values.index[-1], df_pred.index[0]],
        [values.values[-1], df_pred.values[0]],
        color=theme.up_color,
        linestyle="--",
    )
    ax.plot(df_pred.index, df_pred, color=theme.up_color)
    ax.axvspan(values.index[-1], df_pred.index[-1], alpha=0.2)
    _, _, ymin, ymax = plt.axis()
    ax.vlines(values.index[-1], ymin, ymax, linestyle="--")

    # BACKTESTING
    if s_end_date:
        ax.plot(
            df_future.index,
            df_future,
            color=theme.up_color,
            linestyle="--",
        )
        ax.plot(
            [values.index[-1], df_future.index[0]],
            [
                values.values[-1],
                df_future.values[0],
            ],
            color=theme.up_color,
            linestyle="--",
        )

    theme.style_primary_axis(ax)

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
                logger.error("Expected list of one axis item.")
                console.print("[red]Expected list of 1 axis item./n[/red]")
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
        df_pred["Real"] = df_future.values

        if rich_config.USE_COLOR:
            df_pred["Real"] = df_pred["Real"].astype(float)
            df_pred["Prediction"] = df_pred["Prediction"].astype(float)
            df_pred["Dif"] = 100 * (df_pred.Prediction - df_pred.Real) / df_pred.Real
            print_rich_table(
                df_pred,
                headers=["Predicted", "Actual", "% Difference"],
                index_name="Date",
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
