import argparse
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
from sklearn import neighbors
from TimeSeriesCrossValidation import splitTrain
from gamestonk_terminal.helper_funcs import (
    check_positive,
    get_next_stock_market_days,
    parse_known_args_and_warn,
)

register_matplotlib_converters()


# pylint: disable=unused-argument
def k_nearest_neighbors(l_args, s_ticker, s_interval, df_stock):
    parser = argparse.ArgumentParser(
        prog="knn",
        description="""
            K nearest neighbors is a simple algorithm that stores all
            available cases and predict the numerical target based on a similarity measure
            (e.g. distance functions).
        """,
    )

    parser.add_argument(
        "-i",
        "--input",
        action="store",
        dest="n_inputs",
        type=check_positive,
        default=40,
        help="number of days to use for prediction.",
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
        "-j",
        "--jumps",
        action="store",
        dest="n_jumps",
        type=check_positive,
        default=1,
        help="number of jumps in training data.",
    )
    parser.add_argument(
        "-n",
        "--neighbors",
        action="store",
        dest="n_neighbors",
        type=check_positive,
        default=20,
        help="number of neighbors to use on the algorithm.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, l_args)

        # Split training data
        stock_x, stock_y = splitTrain.split_train(
            df_stock["5. adjusted close"].values,
            ns_parser.n_inputs,
            ns_parser.n_days,
            ns_parser.n_jumps,
        )

        # Machine Learning model
        knn = neighbors.KNeighborsRegressor(n_neighbors=ns_parser.n_neighbors)
        knn.fit(stock_x, stock_y)

        # Prediction data
        l_predictions = knn.predict(
            df_stock["5. adjusted close"].values[-ns_parser.n_inputs :].reshape(1, -1)
        )[0]
        l_pred_days = get_next_stock_market_days(
            last_stock_day=df_stock["5. adjusted close"].index[-1],
            n_next_days=ns_parser.n_days,
        )
        df_pred = pd.Series(l_predictions, index=l_pred_days, name="Price")

        # Plotting
        plt.figure()
        plt.plot(df_stock.index, df_stock["5. adjusted close"], lw=2)
        plt.title(
            f"{ns_parser.n_neighbors}-Nearest Neighbors on {s_ticker} - {ns_parser.n_days} days prediction"
        )
        plt.xlim(
            df_stock.index[0], get_next_stock_market_days(df_pred.index[-1], 1)[-1]
        )
        plt.xlabel("Time")
        plt.ylabel("Share Price ($)")
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        plt.minorticks_on()
        plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
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
        plt.ion()
        plt.show()

        # Print prediction data
        print("Predicted share price:")
        df_pred = df_pred.apply(lambda x: f"{x:.2f} $")
        print(df_pred.to_string())
        print("")

    except Exception as e:
        print(e)
        print("")
