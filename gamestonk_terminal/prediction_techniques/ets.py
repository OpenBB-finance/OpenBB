import argparse
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import pmdarima
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from gamestonk_terminal.helper_funcs import (
    check_positive,
    get_next_stock_market_days,
    parse_known_args_and_warn,
    print_pretty_prediction,
)

register_matplotlib_converters()

trend = "Ad"  # Additive damped, A Additive, N None
seasonal = "N"  # None, A Additive, M Multiplicative
seasonal_periods = 5


def check_valid_trend(trend: str) -> str:
    if trend == "N" or trend == "A" or trend == "Ad":
        return trend
    raise argparse.ArgumentTypeError(
        "Invalid trend selected. Choose between 'N', 'A', and 'Ad'"
    )


def check_valid_seasonal(seasonal: str) -> str:
    if seasonal == "N" or seasonal == "A" or seasonal == "M":
        return seasonal
    raise argparse.ArgumentTypeError(
        "Invalid seasonal selected. Choose between 'N', 'A', and 'M'"
    )


def exponential_smoothing(l_args, s_ticker, df_stock):
    parser = argparse.ArgumentParser(
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

    try:
        ns_parser = parse_known_args_and_warn(parser, l_args)

        model, title = get_exponential_smoothing_model(
            df_stock["5. adjusted close"].values,
            ns_parser.trend,
            ns_parser.seasonal,
            ns_parser.seasonal_periods,
        )

        if model.mle_retvals.success:
            forecast = model.forecast(ns_parser.n_days)

            l_pred_days = get_next_stock_market_days(
                last_stock_day=df_stock["5. adjusted close"].index[-1],
                n_next_days=ns_parser.n_days,
            )
            df_pred = pd.Series(forecast, index=l_pred_days, name="Price")

            if ~np.isnan(forecast).any():

                print(f"\n{title}")
                print(f"\nFit model parameters:")
                for key, value in model.params.items():
                    print(f"{key} {' '*(18-len(key))}: {value}")

                print(f"\nAssess fit model:")
                print(f"AIC: {round(model.aic, 2)}")
                print(f"BIC: {round(model.bic, 2)}")
                print(f"SSE: {round(model.sse, 2)}\n")

                # Plotting
                plt.figure()
                plt.plot(df_stock.index, df_stock["5. adjusted close"], lw=2)
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
                    [df_stock["5. adjusted close"].values[-1], df_pred.values[0]],
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
                plt.ion()
                plt.show()

                # Print prediction data
                print_pretty_prediction(
                    df_pred, df_stock["5. adjusted close"].values[-1]
                )
                print("")

            else:
                print("RuntimeWarning: invalid value encountered in double_scalars.")
        else:
            print("ConvergenceWarning: Optimization failed to converge.")

    except Exception as e:
        print(e)
        print("")


def get_exponential_smoothing_model(data, trend, seasonal, seasonal_periods):
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
