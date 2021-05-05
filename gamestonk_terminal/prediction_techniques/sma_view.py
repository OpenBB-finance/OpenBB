""" SMA View"""
__docformat__ = "numpy"

import argparse
from typing import List
import datetime
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters

from gamestonk_terminal.helper_funcs import (
    check_positive,
    parse_known_args_and_warn,
    valid_date,
    patch_pandas_text_adjustment,
    get_next_stock_market_days,
    plot_autoscale,
)

from gamestonk_terminal.prediction_techniques.pred_helper import (
    print_pretty_prediction,
    price_prediction_backtesting_color,
    print_prediction_kpis,
)

from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff

register_matplotlib_converters()


# pylint: disable=unused-argument
def simple_moving_average(other_args: List[str], s_ticker: str, df_stock: pd.DataFrame):
    """
    Run an SMA model
    Parameters
    ----------
    other_args: List[str]
        Argparse arguments
    s_ticker: str
        Stock ticker
    df_stock: pd.DataFrame
        Dataframe of stock prices

    Returns
    -------

    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="sma",
        description="""
            Moving Averages are used to smooth the data in an array to
            help eliminate noise and identify trends. The Simple Moving Average is literally
            the simplest form of a moving average. Each output value is the average of the
            previous n values. In a Simple Moving Average, each value in the time period carries
            equal weight, and values outside of the time period are not included in the average.
            This makes it less responsive to recent changes in the data, which can be useful for
            filtering out those changes.
        """,
    )

    parser.add_argument(
        "-l",
        "--length",
        action="store",
        dest="n_length",
        type=check_positive,
        default=20,
        help="length of SMA window.",
    )
    parser.add_argument(
        "-d",
        "--days",
        action="store",
        dest="n_days",
        type=check_positive,
        default=5,
        help="prediction days.",
    )
    parser.add_argument(
        "-e",
        "--end",
        action="store",
        type=valid_date,
        dest="s_end_date",
        default=None,
        help="The end date (format YYYY-MM-DD) to select - Backtesting",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        # BACKTESTING
        if ns_parser.s_end_date:

            if ns_parser.s_end_date < df_stock.index[0]:
                print(
                    "Backtesting not allowed, since End Date is older than Start Date of historical data\n"
                )
                return

            if (
                ns_parser.s_end_date
                < get_next_stock_market_days(
                    last_stock_day=df_stock.index[0], n_next_days=5 + ns_parser.n_days
                )[-1]
            ):
                print(
                    "Backtesting not allowed, since End Date is too close to Start Date to train model\n"
                )
                return

            future_index = get_next_stock_market_days(
                last_stock_day=ns_parser.s_end_date, n_next_days=ns_parser.n_days
            )

            if future_index[-1] > datetime.datetime.now():
                print(
                    "Backtesting not allowed, since End Date + Prediction days is in the future\n"
                )
                return

            df_future = df_stock[future_index[0] : future_index[-1]]
            df_stock = df_stock[: ns_parser.s_end_date]

        # Prediction data
        l_predictions = list()  # type: List
        for pred_day in range(ns_parser.n_days):
            if pred_day < ns_parser.n_length:
                l_ma_stock = df_stock["5. adjusted close"].values[
                    -ns_parser.n_length + pred_day :
                ]
            else:
                l_ma_stock = list()
            l_predictions.append(np.mean(np.append(l_ma_stock, l_predictions)))

        l_pred_days = get_next_stock_market_days(
            last_stock_day=df_stock["5. adjusted close"].index[-1],
            n_next_days=ns_parser.n_days,
        )
        df_pred = pd.Series(l_predictions, index=l_pred_days, name="Price")

        # Plotting
        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)
        plt.plot(df_stock.index, df_stock["5. adjusted close"], lw=2)
        # BACKTESTING
        if ns_parser.s_end_date:
            plt.title(
                f"BACKTESTING: {ns_parser.n_length} Moving Average on {s_ticker} - {ns_parser.n_days} days prediction"
            )
        else:
            plt.title(
                f"{ns_parser.n_length} Moving Average on {s_ticker} - {ns_parser.n_days} days prediction"
            )
        plt.xlim(
            df_stock.index[0], get_next_stock_market_days(df_pred.index[-1], 1)[-1]
        )
        plt.xlabel("Time")
        plt.ylabel("Share Price ($)")
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        plt.minorticks_on()
        plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
        df_ma = df_stock["5. adjusted close"].rolling(window=ns_parser.n_length).mean()
        plt.plot(df_ma.index, df_ma, lw=2, linestyle="--", c="tab:orange")
        plt.plot(
            [df_stock.index[-1], df_pred.index[0]],
            [df_stock["5. adjusted close"].values[-1], df_pred.values[0]],
            lw=1,
            c="tab:green",
            linestyle="--",
        )
        plt.plot(df_pred.index, df_pred, lw=2, c="tab:green")
        plt.axvspan(
            df_stock.index[-1], df_pred.index[-1], facecolor="tab:orange", alpha=0.2
        )
        _, _, ymin, ymax = plt.axis()
        plt.vlines(
            df_stock.index[-1], ymin, ymax, linewidth=1, linestyle="--", color="k"
        )

        # BACKTESTING
        if ns_parser.s_end_date:
            plt.plot(
                df_future.index,
                df_future["5. adjusted close"],
                lw=2,
                c="tab:blue",
                ls="--",
            )
            plt.plot(
                [df_stock.index[-1], df_future.index[0]],
                [
                    df_stock["5. adjusted close"].values[-1],
                    df_future["5. adjusted close"].values[0],
                ],
                lw=1,
                c="tab:blue",
                linestyle="--",
            )

        if gtff.USE_ION:
            plt.ion()

        plt.show()

        # BACKTESTING
        if ns_parser.s_end_date:
            plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)
            plt.subplot(211)
            plt.plot(
                df_future.index,
                df_future["5. adjusted close"],
                lw=2,
                c="tab:blue",
                ls="--",
            )
            plt.plot(df_pred.index, df_pred, lw=2, c="green")
            plt.scatter(
                df_future.index, df_future["5. adjusted close"], c="tab:blue", lw=3
            )
            plt.plot(
                [df_stock.index[-1], df_future.index[0]],
                [
                    df_stock["5. adjusted close"].values[-1],
                    df_future["5. adjusted close"].values[0],
                ],
                lw=2,
                c="tab:blue",
                ls="--",
            )
            plt.scatter(df_pred.index, df_pred, c="green", lw=3)
            plt.plot(
                [df_stock.index[-1], df_pred.index[0]],
                [df_stock["5. adjusted close"].values[-1], df_pred.values[0]],
                lw=2,
                c="green",
                ls="--",
            )
            plt.title("BACKTESTING: Real data price versus Prediction")
            plt.xlim(df_stock.index[-1], df_pred.index[-1] + datetime.timedelta(days=1))
            plt.xticks(
                [df_stock.index[-1], df_pred.index[-1] + datetime.timedelta(days=1)],
                visible=True,
            )
            plt.ylabel("Share Price ($)")
            plt.grid(b=True, which="major", color="#666666", linestyle="-")
            plt.minorticks_on()
            plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
            plt.legend(["Real data", "Prediction data"])
            plt.xticks([])

            plt.subplot(212)
            plt.axhline(y=0, color="k", linestyle="--", linewidth=2)
            plt.plot(
                df_future.index,
                100
                * (df_pred.values - df_future["5. adjusted close"].values)
                / df_future["5. adjusted close"].values,
                lw=2,
                c="red",
            )
            plt.scatter(
                df_future.index,
                100
                * (df_pred.values - df_future["5. adjusted close"].values)
                / df_future["5. adjusted close"].values,
                c="red",
                lw=5,
            )
            plt.title("BACKTESTING: Error between Real data and Prediction [%]")
            plt.plot(
                [df_stock.index[-1], df_future.index[0]],
                [
                    0,
                    100
                    * (df_pred.values[0] - df_future["5. adjusted close"].values[0])
                    / df_future["5. adjusted close"].values[0],
                ],
                lw=2,
                ls="--",
                c="red",
            )
            plt.xlim(df_stock.index[-1], df_pred.index[-1] + datetime.timedelta(days=1))
            plt.xticks(
                [df_stock.index[-1], df_pred.index[-1] + datetime.timedelta(days=1)],
                visible=True,
            )
            plt.xlabel("Time")
            plt.ylabel("Prediction Error (%)")
            plt.grid(b=True, which="major", color="#666666", linestyle="-")
            plt.minorticks_on()
            plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
            plt.legend(["Real data", "Prediction data"])

            if gtff.USE_ION:
                plt.ion()

            plt.show()

            # Refactor prediction dataframe for backtesting print
            df_pred.name = "Prediction"
            df_pred = df_pred.to_frame()
            df_pred["Real"] = df_future["5. adjusted close"]

            if gtff.USE_COLOR:

                patch_pandas_text_adjustment()

                print("Time         Real [$]  x  Prediction [$]")
                print(
                    df_pred.apply(
                        price_prediction_backtesting_color, axis=1
                    ).to_string()
                )
            else:
                print(df_pred[["Real", "Prediction"]].round(2).to_string())

            print("")
            print_prediction_kpis(df_pred["Real"].values, df_pred["Prediction"].values)

        else:
            # Print prediction data
            print_pretty_prediction(df_pred, df_stock["5. adjusted close"].values[-1])
        print("")

    except Exception as e:
        print(e)
        print("")
