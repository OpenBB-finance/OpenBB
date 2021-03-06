import argparse
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import pmdarima
from statsmodels.tsa.arima.model import ARIMA
from gamestonk_terminal.helper_funcs import (
    check_positive,
    get_next_stock_market_days,
    parse_known_args_and_warn,
)

register_matplotlib_converters()


# pylint: disable=unused-argument
def arima(l_args, s_ticker, df_stock):
    parser = argparse.ArgumentParser(
        prog="arima",
        description="""
            In statistics and econometrics, and in particular in time series analysis, an
            autoregressive integrated moving average (ARIMA) model is a generalization of an
            autoregressive moving average (ARMA) model. Both of these models are fitted to time
            series data either to better understand the data or to predict future points in the
            series (forecasting). ARIMA(p,d,q) where parameters p, d, and q are non-negative
            integers, p is the order (number of time lags) of the autoregressive model, d is the
            degree of differencing (the number of times the data have had past values subtracted),
            and q is the order of the moving-average model.
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
        "-i",
        "--ic",
        action="store",
        dest="s_ic",
        type=str,
        default="aic",
        choices=["aic", "aicc", "bic", "hqic", "oob"],
        help="information criteria.",
    )
    parser.add_argument(
        "-s",
        "--seasonal",
        action="store_true",
        default=False,
        dest="b_seasonal",
        help="Use weekly seasonal data.",
    )
    parser.add_argument(
        "-o",
        "--order",
        action="store",
        dest="s_order",
        type=str,
        help="arima model order (p,d,q) in format: pdq.",
    )
    parser.add_argument(
        "-r",
        "--results",
        action="store_true",
        dest="b_results",
        default=False,
        help="results about ARIMA summary flag.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, l_args)

        # Machine Learning model
        if ns_parser.s_order:
            t_order = tuple([int(ord) for ord in list(ns_parser.s_order)])
            model = ARIMA(df_stock["5. adjusted close"].values, order=t_order).fit()
            l_predictions = model.predict(
                start=len(df_stock["5. adjusted close"]) + 1,
                end=len(df_stock["5. adjusted close"]) + ns_parser.n_days,
            )
        else:
            if ns_parser.b_seasonal:
                model = pmdarima.auto_arima(
                    df_stock["5. adjusted close"].values,
                    error_action="ignore",
                    seasonal=True,
                    m=5,
                    information_criteria=ns_parser.s_ic,
                )
            else:
                model = pmdarima.auto_arima(
                    df_stock["5. adjusted close"].values,
                    error_action="ignore",
                    seasonal=False,
                    information_criteria=ns_parser.s_ic,
                )
            l_predictions = model.predict(n_periods=ns_parser.n_days)

        # Prediction data
        l_pred_days = get_next_stock_market_days(
            last_stock_day=df_stock["5. adjusted close"].index[-1],
            n_next_days=ns_parser.n_days,
        )
        df_pred = pd.Series(l_predictions, index=l_pred_days, name="Price")

        if ns_parser.b_results:
            print(model.summary())
            print("")

        # Plotting
        plt.plot(df_stock.index, df_stock["5. adjusted close"], lw=2)
        if ns_parser.s_order:
            plt.title(
                f"ARIMA {str(t_order)} on {s_ticker} - {ns_parser.n_days} days prediction"
            )
        else:
            plt.title(
                f"ARIMA {model.order} on {s_ticker} - {ns_parser.n_days} days prediction"
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
