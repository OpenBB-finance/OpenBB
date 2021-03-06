import argparse
import warnings
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
from fbprophet import Prophet
from gamestonk_terminal.helper_funcs import (
    check_positive,
    get_next_stock_market_days,
    parse_known_args_and_warn,
)

register_matplotlib_converters()

warnings.simplefilter("ignore")


def fbprophet(l_args, s_ticker, df_stock):
    parser = argparse.ArgumentParser(
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

    try:
        ns_parser = parse_known_args_and_warn(parser, l_args)

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

        _, ax = plt.subplots()
        model.plot(forecast, ax=ax, xlabel="Time", ylabel="Share Price ($)")
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
        plt.title(f"Fb Prophet on {s_ticker} - {ns_parser.n_days} days prediction")
        plt.ion()
        plt.show()

        print("")
        print("Predicted share price:")
        df_pred = forecast["yhat"][-ns_parser.n_days :].apply(lambda x: f"{x:.2f} $")
        df_pred.index = l_pred_days
        print(df_pred.to_string())
        print("")

    except Exception as e:
        print(e)
        print("")
