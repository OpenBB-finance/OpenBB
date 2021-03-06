import argparse
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
from TimeSeriesCrossValidation import splitTrain
from sklearn import linear_model
from sklearn import pipeline
from sklearn import preprocessing

from gamestonk_terminal.helper_funcs import check_positive, get_next_stock_market_days

register_matplotlib_converters()

USER_INPUT = 0
LINEAR = 1
QUADRATIC = 2
CUBIC = 3


# -------------------------------------------------- REGRESSION --------------------------------------------------
# pylint: disable=unused-argument
def regression(l_args, s_ticker, s_interval, df_stock, polynomial):
    parser = argparse.ArgumentParser(
        prog="regression",
        description="""
            Regression attempts to model the relationship between
            two variables by fitting a linear/quadratic/cubic/other equation to
            observed data. One variable is considered to be an explanatory variable,
            and the other is considered to be a dependent variable.
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

    if polynomial == USER_INPUT:
        parser.add_argument(
            "-p",
            "--polynomial",
            action="store",
            dest="n_polynomial",
            type=check_positive,
            required=True,
            help="polynomial associated with regression.",
        )

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        # Split training data
        stock_x, stock_y = splitTrain.split_train(
            df_stock["5. adjusted close"].values,
            ns_parser.n_inputs,
            ns_parser.n_days,
            ns_parser.n_jumps,
        )

        # Machine Learning model
        if polynomial == LINEAR:
            model = linear_model.LinearRegression(n_jobs=-1)
        else:
            if polynomial == USER_INPUT:
                polynomial = ns_parser.n_polynomial
            model = pipeline.make_pipeline(
                preprocessing.PolynomialFeatures(polynomial), linear_model.Ridge()
            )

        model.fit(stock_x, stock_y)
        l_predictions = model.predict(
            df_stock["5. adjusted close"].values[-ns_parser.n_inputs :].reshape(1, -1)
        )[0]

        # Prediction data
        l_pred_days = get_next_stock_market_days(
            last_stock_day=df_stock["5. adjusted close"].index[-1],
            n_next_days=ns_parser.n_days,
        )
        df_pred = pd.Series(l_predictions, index=l_pred_days, name="Price")

        # Plotting
        plt.plot(df_stock.index, df_stock["5. adjusted close"], lw=2)
        plt.title(
            f"Regression (polynomial {polynomial}) on {s_ticker} - {ns_parser.n_days} days prediction"
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
        plt.show()

        # Print prediction data
        print("Predicted share price:")
        df_pred = df_pred.apply(lambda x: f"{x:.2f} $")
        print(df_pred.to_string())
        print("")

    except Exception as e:
        print(e)
        print("")
