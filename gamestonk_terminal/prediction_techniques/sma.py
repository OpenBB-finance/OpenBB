import argparse
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters

from gamestonk_terminal.helper_funcs import check_positive, get_next_stock_market_days

register_matplotlib_converters()


# ----------------------------------------------------- SMA -----------------------------------------------------
# pylint: disable=unused-argument
def simple_moving_average(l_args, s_ticker, s_interval, df_stock):
    parser = argparse.ArgumentParser(
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

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        # Prediction data
        l_predictions = list()
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
        plt.plot(df_stock.index, df_stock["5. adjusted close"], lw=2)
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
        plt.show()

        # Print prediction data
        print("Predicted share price:")
        df_pred = df_pred.apply(lambda x: f"{x:.2f} $")
        print(df_pred.to_string())
        print("")

    except Exception as e:
        print(e)
        print("")
