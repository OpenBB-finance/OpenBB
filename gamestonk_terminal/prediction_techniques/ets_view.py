""" ets model view """
__docformat__ = "numpy"

import argparse
from typing import List, Union
import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters
from statsmodels.tsa.holtwinters import ExponentialSmoothing

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

# trend = "Ad"  # Additive damped, A Additive, N None
# seasonal = "N"  # None, A Additive, M Multiplicative
# seasonal_periods = 5


def check_valid_trend(trend: str) -> str:
    if trend in ("N", "A", "Ad"):
        return trend
    raise argparse.ArgumentTypeError(
        "Invalid trend selected. Choose between 'N', 'A', and 'Ad'"
    )


def check_valid_seasonal(seasonal: str) -> str:
    if seasonal in ("N", "A", "M"):
        return seasonal
    raise argparse.ArgumentTypeError(
        "Invalid seasonal selected. Choose between 'N', 'A', and 'M'"
    )


def exponential_smoothing(other_args: List[str], s_ticker: str, df_stock: pd.DataFrame):
    """
    Perform exponential smoothing forecasting
    Parameters
    ----------
    other_args: List[str]
        Argparse arguments
    s_ticker: str
        Loaded ticker
    df_stock: pd.DataFrame
        Loaded stock dataframe

    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="ets",
        description="""
            Exponential Smoothing, see https://otexts.com/fpp2/taxonomy.html

            Trend='N',  Seasonal='N': Simple Exponential Smoothing
            Trend='N',  Seasonal='A': Exponential Smoothing
            Trend='N',  Seasonal='M': Exponential Smoothing
            Trend='A',  Seasonal='N': Holt’s linear method
            Trend='A',  Seasonal='A': Additive Holt-Winters’ method
            Trend='A',  Seasonal='M': Multiplicative Holt-Winters’ method
            Trend='Ad', Seasonal='N': Additive damped trend method
            Trend='Ad', Seasonal='A': Exponential Smoothing
            Trend='Ad', Seasonal='M': Holt-Winters’ damped method
            Trend component: N: None, A: Additive, Ad: Additive Damped
            Seasonality component: N: None, A: Additive, M: Multiplicative
        """,
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
        "-t",
        "--trend",
        action="store",
        dest="trend",
        type=check_valid_trend,
        default="N",
        help="Trend component: N: None, A: Additive, Ad: Additive Damped.",
    )
    parser.add_argument(
        "-s",
        "--seasonal",
        action="store",
        dest="seasonal",
        type=check_valid_seasonal,
        default="N",
        help="Seasonality component: N: None, A: Additive, M: Multiplicative.",
    )
    parser.add_argument(
        "-p",
        "--periods",
        action="store",
        dest="seasonal_periods",
        type=check_positive,
        default=5,
        help="Seasonal periods.",
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

        # Get ETS model
        model, title = get_exponential_smoothing_model(
            df_stock["Adj Close"].values,
            ns_parser.trend,
            ns_parser.seasonal,
            ns_parser.seasonal_periods,
        )

        if model.mle_retvals.success:
            forecast = [i if i > 0 else 0 for i in model.forecast(ns_parser.n_days)]

            l_pred_days = get_next_stock_market_days(
                last_stock_day=df_stock["Adj Close"].index[-1],
                n_next_days=ns_parser.n_days,
            )
            df_pred = pd.Series(forecast, index=l_pred_days, name="Price")

            if ~np.isnan(forecast).any():

                print(f"\n{title}")
                print("\nFit model parameters:")
                for key, value in model.params.items():
                    print(f"{key} {' '*(18-len(key))}: {value}")

                print("\nAssess fit model:")
                print(f"AIC: {round(model.aic, 2)}")
                print(f"BIC: {round(model.bic, 2)}")
                print(f"SSE: {round(model.sse, 2)}\n")

                # Plotting
                plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)
                plt.plot(df_stock.index, df_stock["Adj Close"], lw=2)
                # BACKTESTING
                if ns_parser.s_end_date:
                    plt.title(f"BACKTESTING: {title} on {s_ticker}")
                else:
                    plt.title(f"{title} on {s_ticker}")

                plt.xlim(
                    df_stock.index[0],
                    get_next_stock_market_days(df_pred.index[-1], 1)[-1],
                )
                plt.xlabel("Time")
                plt.ylabel("Share Price ($)")
                plt.grid(b=True, which="major", color="#666666", linestyle="-")
                plt.minorticks_on()
                plt.grid(
                    b=True, which="minor", color="#999999", linestyle="-", alpha=0.2
                )
                plt.plot(
                    [df_stock.index[-1], df_pred.index[0]],
                    [df_stock["Adj Close"].values[-1], df_pred.values[0]],
                    lw=1,
                    c="tab:green",
                    linestyle="--",
                )
                plt.plot(df_pred.index, df_pred, lw=2, c="tab:green")
                plt.axvspan(
                    df_stock.index[-1],
                    df_pred.index[-1],
                    facecolor="tab:orange",
                    alpha=0.2,
                )
                _, _, ymin, ymax = plt.axis()
                plt.vlines(
                    df_stock.index[-1],
                    ymin,
                    ymax,
                    linewidth=1,
                    linestyle="--",
                    color="k",
                )

                # BACKTESTING
                if ns_parser.s_end_date:
                    plt.plot(
                        df_future.index,
                        df_future["Adj Close"],
                        lw=2,
                        c="tab:blue",
                        ls="--",
                    )
                    plt.plot(
                        [df_stock.index[-1], df_future.index[0]],
                        [
                            df_stock["Adj Close"].values[-1],
                            df_future["Adj Close"].values[0],
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
                        df_future["Adj Close"],
                        lw=2,
                        c="tab:blue",
                        ls="--",
                    )
                    plt.plot(df_pred.index, df_pred, lw=2, c="green")
                    plt.scatter(
                        df_future.index,
                        df_future["Adj Close"],
                        c="tab:blue",
                        lw=3,
                    )
                    plt.plot(
                        [df_stock.index[-1], df_future.index[0]],
                        [
                            df_stock["Adj Close"].values[-1],
                            df_future["Adj Close"].values[0],
                        ],
                        lw=2,
                        c="tab:blue",
                        ls="--",
                    )
                    plt.scatter(df_pred.index, df_pred, c="green", lw=3)
                    plt.plot(
                        [df_stock.index[-1], df_pred.index[0]],
                        [df_stock["Adj Close"].values[-1], df_pred.values[0]],
                        lw=2,
                        c="green",
                        ls="--",
                    )
                    plt.title("BACKTESTING: Real data price versus Prediction")
                    plt.xlim(
                        df_stock.index[-1],
                        df_pred.index[-1] + datetime.timedelta(days=1),
                    )
                    plt.ylabel("Share Price ($)")
                    plt.grid(b=True, which="major", color="#666666", linestyle="-")
                    plt.minorticks_on()
                    plt.grid(
                        b=True, which="minor", color="#999999", linestyle="-", alpha=0.2
                    )
                    plt.legend(["Real data", "Prediction data"])
                    plt.xticks([])

                    plt.subplot(212)
                    plt.axhline(y=0, color="k", linestyle="--", linewidth=2)
                    plt.plot(
                        df_future.index,
                        100
                        * (df_pred.values - df_future["Adj Close"].values)
                        / df_future["Adj Close"].values,
                        lw=2,
                        c="red",
                    )
                    plt.scatter(
                        df_future.index,
                        100
                        * (df_pred.values - df_future["Adj Close"].values)
                        / df_future["Adj Close"].values,
                        c="red",
                        lw=5,
                    )
                    plt.title("BACKTESTING: Error between Real data and Prediction [%]")
                    plt.plot(
                        [df_stock.index[-1], df_future.index[0]],
                        [
                            0,
                            100
                            * (df_pred.values[0] - df_future["Adj Close"].values[0])
                            / df_future["Adj Close"].values[0],
                        ],
                        lw=2,
                        ls="--",
                        c="red",
                    )
                    plt.xlim(
                        df_stock.index[-1],
                        df_pred.index[-1] + datetime.timedelta(days=1),
                    )
                    plt.xlabel("Time")
                    plt.ylabel("Prediction Error (%)")
                    plt.grid(b=True, which="major", color="#666666", linestyle="-")
                    plt.minorticks_on()
                    plt.grid(
                        b=True, which="minor", color="#999999", linestyle="-", alpha=0.2
                    )
                    plt.legend(["Real data", "Prediction data"])

                    if gtff.USE_ION:
                        plt.ion()

                    plt.show()

                    # Refactor prediction dataframe for backtesting print
                    df_pred.name = "Prediction"
                    df_pred = df_pred.to_frame()
                    df_pred["Real"] = df_future["Adj Close"]

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
                    print_prediction_kpis(
                        df_pred["Real"].values, df_pred["Prediction"].values
                    )

                else:
                    # Print prediction data
                    print_pretty_prediction(df_pred, df_stock["Adj Close"].values[-1])
                print("")

            else:
                print("RuntimeWarning: invalid value encountered in double_scalars.")
        else:
            print("ConvergenceWarning: Optimization failed to converge.")

    except Exception as e:
        print(e)
        print("")


def get_exponential_smoothing_model(
    data: Union[pd.Series, np.ndarray], trend, seasonal, seasonal_periods
):
    """
    Perform exponential smoothing
    Parameters
    ----------
    data: Union[pd.Series, np.ndarray]
        Series of closing values
    trend: str
        Trend component.  One of [N, A, Ad]
    seasonal: str
        Seasonal component.  One of [N, A, M]
    seasonal_periods: int
        Number of seaosnal periods in a year


    Returns
    -------
    model:
        Exponential smoothing model
    title: str
        String describing selected model
    """
    if trend == "N":  # None
        if seasonal == "N":  # None
            title = "Trend='N',  Seasonal='N': Simple Exponential Smoothing"
            ETS = ExponentialSmoothing(
                data,
                trend=None,
                damped_trend=False,
                seasonal=None,
            )
            model = ETS.fit(
                smoothing_level=None, smoothing_trend=None, damping_trend=None
            )

        elif seasonal == "A":  # Additive
            title = "Trend='N',  Seasonal='A': Exponential Smoothing"
            ETS = ExponentialSmoothing(
                data,
                trend=None,
                damped_trend=False,
                seasonal="add",
                seasonal_periods=seasonal_periods,
            )
            model = ETS.fit(smoothing_level=None, smoothing_seasonal=None)

        elif seasonal == "M":  # Multiplicative
            title = "Trend='N',  Seasonal='M': Exponential Smoothing"
            ETS = ExponentialSmoothing(
                data,
                trend=None,
                damped_trend=False,
                seasonal="mul",
                seasonal_periods=seasonal_periods,
            )
            model = ETS.fit(smoothing_level=None, smoothing_seasonal=None)

    elif trend == "A":  # Additive
        if seasonal == "N":  # None
            title = "Trend='A',  Seasonal='N': Holt’s linear method"
            ETS = ExponentialSmoothing(
                data,
                trend="add",
                damped_trend=False,
                seasonal=None,
            )
            model = ETS.fit(
                smoothing_level=None, smoothing_trend=None, damping_trend=None
            )

        elif seasonal == "A":  # Additive
            title = "Trend='A',  Seasonal='A': Additive Holt-Winters’ method"
            ETS = ExponentialSmoothing(
                data,
                trend="add",
                damped_trend=False,
                seasonal="add",
                seasonal_periods=seasonal_periods,
            )
            model = ETS.fit(
                smoothing_level=None, smoothing_trend=None, smoothing_seasonal=None
            )

        elif seasonal == "M":  # Multiplicative
            title = "Trend='A',  Seasonal='M': Multiplicative Holt-Winters’ method"
            ETS = ExponentialSmoothing(
                data,
                trend="add",
                damped_trend=False,
                seasonal="mul",
                seasonal_periods=seasonal_periods,
            )
            model = ETS.fit(
                smoothing_level=None, smoothing_trend=None, smoothing_seasonal=None
            )

    elif trend == "Ad":  # Additive damped
        if seasonal == "N":  # None
            title = "Trend='Ad', Seasonal='N': Additive damped trend method"
            ETS = ExponentialSmoothing(
                data,
                trend="add",
                damped_trend=True,
                seasonal=None,
            )
            model = ETS.fit(
                smoothing_level=None, smoothing_trend=None, damping_trend=None
            )

        elif seasonal == "A":  # Additive
            title = "Trend='Ad', Seasonal='A': Exponential Smoothing"
            ETS = ExponentialSmoothing(
                data,
                trend="add",
                damped_trend=True,
                seasonal="add",
                seasonal_periods=seasonal_periods,
            )
            model = ETS.fit(
                smoothing_level=None,
                smoothing_trend=None,
                damping_trend=None,
                smoothing_seasonal=None,
            )

        elif seasonal == "M":  # Multiplicative
            title = "Trend='Ad', Seasonal='M': Holt-Winters’ damped method"
            ETS = ExponentialSmoothing(
                data,
                trend="add",
                damped_trend=True,
                seasonal="mul",
                seasonal_periods=seasonal_periods,
            )
            model = ETS.fit(
                smoothing_level=None,
                smoothing_trend=None,
                damping_trend=None,
                smoothing_seasonal=None,
            )

    return model, title
