"""options info. [Source: Yahoo Finance]."""
import argparse
from bisect import bisect_left
import yfinance as yf
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    valid_date,
)


def volume_graph(s_ticker, l_args):
    """Show traded options volume. [Source: Yahoo Finance]."""
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="volume",
        description="""Display volume graph for a date. [Source: Yahoo Finance].""",
    )
    parser.add_argument(
        "-e",
        "--expiry",
        type=valid_date,
        dest="s_expiry_date",
        help="The expiry date (format YYYY-MM-DD) for the option chain",
        required=True,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, l_args)
        if not ns_parser:
            return

        __get_volume_graph(s_ticker, ns_parser.s_expiry_date.strftime("%Y-%m-%d"))

    except SystemExit:
        print("")
    except Exception as e:
        print(e)


def __get_volume_graph(ticker_name, volume_percentile_threshold=50):
    # SET VOLUME TO BE FILTERED, default = 50
    PERCENTILE_THRESHOLD = volume_percentile_threshold

    TICKER_NAME = ticker_name
    raw_data_options = yf.Ticker(TICKER_NAME)
    EXP_DATE = __get_exp_data(raw_data_options)

    # current stock price
    spot = __get_current_spot(raw_data_options)

    calls = __parse_opt_data(raw_data_options, EXP_DATE)
    puts = __parse_opt_data(raw_data_options, EXP_DATE, is_calls=False)

    calls = __add_max_pain_data(calls, spot)

    puts = __add_max_pain_data(puts, spot, is_calls=False)

    max_pain = __calc_max_pain(calls, puts)

    # Initialize the matplotlib figure
    sns.set_style("darkgrid")
    plt.rcParams["figure.dpi"] = 360
    _, ax = plt.subplots(figsize=(15, 12))
    sns.set_style(style="darkgrid")

    # make x axis symmetric
    axis_origin = max(abs(max(puts["oi+v"])), abs(max(calls["oi+v"])))
    ax.set_xlim(-axis_origin, +axis_origin)

    VOLUME_THRESHOLD = np.percentile(calls["oi+v"], PERCENTILE_THRESHOLD)

    g = sns.barplot(
        x="oi+v",
        y="strike",
        data=calls[calls["oi+v"] > VOLUME_THRESHOLD],
        label="Calls: Open Interest",
        color="lightgreen",
        orient="h",
    )

    g = sns.barplot(
        x="volume",
        y="strike",
        data=calls[calls["oi+v"] > VOLUME_THRESHOLD],
        label="Calls: Volume",
        color="green",
        orient="h",
    )

    g = sns.barplot(
        x="oi+v",
        y="strike",
        data=puts[puts["oi+v"] < -VOLUME_THRESHOLD],
        label="Puts: Open Interest",
        color="pink",
        orient="h",
    )

    g = sns.barplot(
        x="volume",
        y="strike",
        data=puts[puts["oi+v"] < -VOLUME_THRESHOLD],
        label="Puts: Volume",
        color="red",
        orient="h",
    )

    # draw spot line
    s = [float(strike.get_text()) for strike in ax.get_yticklabels()]
    spot_index = bisect_left(s, spot)  # find where the spot is on the graph
    spot_line = ax.axhline(spot_index, ls="--", color="dodgerblue", alpha=0.3)

    # draw max pain line
    max_pain_index = bisect_left(s, max_pain)
    max_pain_line = ax.axhline(max_pain_index, ls="-", color="black", alpha=0.3)
    max_pain_line.set_linewidth(5)

    # ax.axhline(max_pain_index, ls='--')
    # format ticklabels without - for puts
    g.set_xticks(g.get_xticks())
    xlabels = ["{:,.0f}".format(x).replace("-", "") for x in g.get_xticks()]
    g.set_xticklabels(xlabels)

    plt.title(
        f"{TICKER_NAME.upper()} volumes for {EXP_DATE} (open interest displayed only during market hours)"
    )
    ax.invert_yaxis()

    # ax.spines['left'].set_position('center')

    _ = ax.legend()
    handles, _ = ax.get_legend_handles_labels()
    handles.append(spot_line)
    handles.append(max_pain_line)

    # create legend labels + add to graph
    labels = [
        "Calls open interest",
        "Calls volume ",
        "Puts open interest",
        "Puts volume",
        "Current stock price",
        f"Max pain = {max_pain}",
    ]

    plt.legend(handles=handles[:], labels=labels)

    sns.despine(left=True, bottom=True)
    plt.show()


def __add_max_pain_data(df, spot, is_calls=True):
    # max pain parsing + calculation
    df["spot"] = round(spot, 2)
    if is_calls:
        df["dv"] = spot - df.index
    else:
        df["dv"] = df.index - spot
    df["dv"] = df["dv"].apply(lambda x: max(0, x))
    df["dv"] = abs(df["dv"] * df["volume"])
    return df


def __calc_max_pain(calls, puts):

    df = pd.merge(calls, puts, left_index=True, right_index=True)
    df["dv"] = round(df["dv_x"] + df["dv_y"], 2)

    max_pain = df["dv"].idxmax()
    return max_pain


def __parse_opt_data(raw_data_options, exp_date, is_calls=True):
    # get option chain for specific expiration
    opt = raw_data_options.option_chain(exp_date)

    # PARSE DATA
    if is_calls:
        option_data = opt.calls
        flag = "calls"
    else:
        option_data = opt.puts
        flag = "puts"

    data = option_data.pivot_table(
        index="strike", values=["volume", "openInterest"], aggfunc="sum"
    ).reindex()

    data["strike"] = data.index
    data["type"] = flag

    if is_calls:
        data["openInterest"] = data["openInterest"]
        data["volume"] = data["volume"]
    else:
        data["openInterest"] = -data["openInterest"]
        data["volume"] = -data["volume"]

    data["oi+v"] = data["openInterest"] + data["volume"]
    return data


def __get_current_spot(raw_data_options):
    return raw_data_options.history().tail(1)["Close"].iloc[0]


def __get_exp_data(raw_data_options, date_index=0):
    return raw_data_options.options[date_index]
