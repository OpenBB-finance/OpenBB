import argparse
import datetime
import warnings
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
from fbprophet import Prophet
from gamestonk_terminal.helper_funcs import (
    check_positive,
    get_next_stock_market_days,
    parse_known_args_and_warn,
    valid_date,
    patch_pandas_text_adjustment,
    plot_autoscale,
)
from gamestonk_terminal.prediction_techniques.pred_helper import (
    price_prediction_backtesting_color,
    print_prediction_kpis,
)

from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff

register_matplotlib_converters()

warnings.simplefilter("ignore")


def fbprophet(l_args, s_ticker, df_stock):
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="fbprophet",
        description="""
            Facebook Prophet is a forecasting procedure that is fast and provides
            completely automated forecasts that can be tuned by hand by data scientists
            and analysts. It was developed by Facebook's data science team and is open
            source.
        """,
    )

    parser.add_argument(
        "-d",
        "--days",
        action="store",
        dest="n_days",
        type=check_positive,
        default=5,
        help="prediction days",
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
        ns_parser = parse_known_args_and_warn(parser, l_args)
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

        df_stock = df_stock.sort_index(ascending=True)
        df_stock.reset_index(level=0, inplace=True)
        df_stock = df_stock[["date", "5. adjusted close"]]
        df_stock = df_stock.rename(columns={"date": "ds", "5. adjusted close": "y"})
        df_stock["ds"] = pd.to_datetime(df_stock["ds"])

        model = Prophet(yearly_seasonality=False, daily_seasonality=False)
        model.fit(df_stock)

        l_pred_days = get_next_stock_market_days(
            last_stock_day=pd.to_datetime(df_stock["ds"].values[-1]),
            n_next_days=ns_parser.n_days,
        )
        close_prices = model.make_future_dataframe(periods=ns_parser.n_days)
        forecast = model.predict(close_prices)

        df_pred = forecast["yhat"][
            -ns_parser.n_days :
        ]  # .apply(lambda x: f"{x:.2f} $")
        df_pred.index = l_pred_days

        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        model.plot(
            forecast[: -ns_parser.n_days],
            ax=ax,
            xlabel="Time",
            ylabel="Share Price ($)",
        )
        _, _, ymin, ymax = ax.axis()
        ax.vlines(
            df_stock["ds"].values[-1],
            ymin,
            ymax,
            linewidth=2,
            linestyle="--",
            color="k",
        )
        plt.axvspan(
            df_stock["ds"].values[-1],
            l_pred_days[-1],
            facecolor="tab:orange",
            alpha=0.2,
        )
        plt.ylim(ymin, ymax)
        plt.xlim(
            df_stock["ds"].values[0], get_next_stock_market_days(l_pred_days[-1], 1)[-1]
        )
        # BACKTESTING
        if ns_parser.s_end_date:
            plt.title(
                f"BACKTESTING: Fb Prophet on {s_ticker} - {ns_parser.n_days} days prediction"
            )
        else:
            plt.title(f"Fb Prophet on {s_ticker} - {ns_parser.n_days} days prediction")

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
                [df_stock["ds"].values[-1], df_future.index[0]],
                [
                    df_stock["y"].values[-1],
                    df_future["5. adjusted close"].values[0],
                ],
                lw=1,
                c="tab:blue",
                linestyle="--",
            )

        plt.plot(df_pred.index, df_pred.values, lw=2, c="green")

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
                df_future.index,
                df_future["5. adjusted close"],
                c="tab:blue",
                lw=3,
            )
            plt.plot(
                [df_stock["ds"].values[-1], df_future.index[0]],
                [
                    df_stock["y"].values[-1],
                    df_future["5. adjusted close"].values[0],
                ],
                lw=2,
                c="tab:blue",
                ls="--",
            )
            plt.scatter(df_pred.index, df_pred, c="green", lw=3)
            plt.plot(
                [df_stock["ds"].values[-1], df_pred.index[0]],
                [df_stock["y"].values[-1], df_pred.values[0]],
                lw=2,
                c="green",
                ls="--",
            )
            plt.title("BACKTESTING: Real data price versus Prediction")
            plt.xlim(
                df_stock["ds"].values[-1],
                df_pred.index[-1] + datetime.timedelta(days=1),
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
                [df_stock["ds"].values[-1], df_future.index[0]],
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
            plt.xlim(
                df_stock["ds"].values[-1],
                df_pred.index[-1] + datetime.timedelta(days=1),
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
            print("")
            print("Predicted share price:")
            print(df_pred.to_string())
        print("")

    except Exception as e:
        print(e)
        print("")
