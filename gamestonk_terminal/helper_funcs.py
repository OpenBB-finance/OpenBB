import argparse
from datetime import datetime, timedelta, time as Time
import random
import re
import sys
from pytz import timezone
import iso8601
import matplotlib.pyplot as plt
from holidays import US as holidaysUS
from colorama import Fore, Style
import pandas as pd
import pandas.io.formats.format
from pandas._config.config import get_option
from pandas.plotting import register_matplotlib_converters
from gamestonk_terminal import feature_flags as gtff

register_matplotlib_converters()


def check_non_negative(value) -> int:
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError(f"{value} is negative")
    return ivalue


def check_positive(value) -> int:
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(f"{value} is an invalid positive int value")
    return ivalue


def valid_date(s: str) -> datetime:
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError as value_error:
        raise argparse.ArgumentTypeError("Not a valid date: {s}") from value_error


def plot_view_stock(df, symbol):
    df.sort_index(ascending=True, inplace=True)
    _, axVolume = plt.subplots()
    plt.bar(df.index, df.iloc[:, -1], color="k", alpha=0.8, width=0.3)
    plt.ylabel("Volume")
    _ = axVolume.twinx()
    plt.plot(df.index, df.iloc[:, :-1])
    plt.title(symbol + " (Time Series)")
    plt.xlim(df.index[0], df.index[-1])
    plt.xlabel("Time")
    plt.ylabel("Share Price ($)")
    plt.legend(df.columns)
    plt.grid(b=True, which="major", color="#666666", linestyle="-")
    plt.minorticks_on()
    plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)

    if gtff.USE_ION:
        plt.ion()

    plt.show()
    print("")


def b_is_stock_market_open() -> bool:
    """ checks if the stock market is open """
    # Get current US time
    now = datetime.now(timezone("US/Eastern"))
    # Check if it is a weekend
    if now.date().weekday() > 4:
        return False
    # Check if it is a holiday
    if now.strftime("%Y-%m-%d") in holidaysUS():
        return False
    # Check if it hasn't open already
    if now.time() < Time(hour=9, minute=30, second=0):
        return False
    # Check if it has already closed
    if now.time() > Time(hour=16, minute=0, second=0):
        return False
    # Otherwise, Stock Market is open!
    return True


def long_number_format(num) -> str:
    if isinstance(num, float):
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        num_str = int(num) if num.is_integer() else f"{num:.3f}"
        return f"{num_str} {' KMBTP'[magnitude]}".strip()
    if isinstance(num, int):
        num = str(num)
    if num.lstrip("-").isdigit():
        num = int(num)
        num /= 1.0
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        num_str = int(num) if num.is_integer() else f"{num:.3f}"
        return f"{num_str} {' KMBTP'[magnitude]}".strip()
    return num


def clean_data_values_to_float(val: str) -> float:
    # Remove any leading or trailing parentheses and spaces
    val = val.strip("( )")
    if val == "-":
        val = "0"

    # Convert percentage to decimal
    if val.endswith("%"):
        val_as_float = float(val[:-1]) / 100.0
    # Convert from billions
    elif val.endswith("B"):
        val_as_float = float(val[:-1]) * 1_000_000_000
    # Convert from millions
    elif val.endswith("M"):
        val_as_float = float(val[:-1]) * 1_000_000
    # Convert from thousands
    elif val.endswith("K"):
        val_as_float = float(val[:-1]) * 1000
    else:
        val_as_float = float(val)
    return val_as_float


def int_or_round_float(x) -> str:
    if (x - int(x) < -sys.float_info.epsilon) or (x - int(x) > sys.float_info.epsilon):
        return " " + str(round(x, 2))

    return " " + str(int(x))


def divide_chunks(data, n):
    # looping till length of data
    for i in range(0, len(data), n):
        yield data[i : i + n]


def get_next_stock_market_days(last_stock_day, n_next_days) -> list:
    n_days = 0
    l_pred_days = list()
    while n_days < n_next_days:

        last_stock_day += timedelta(hours=24)

        # Check if it is a weekend
        if last_stock_day.date().weekday() > 4:
            continue
        # Check if it is a holiday
        if last_stock_day.strftime("%Y-%m-%d") in holidaysUS():
            continue
        # Otherwise stock market is open
        n_days += 1
        l_pred_days.append(last_stock_day)

    return l_pred_days


def get_data(tweet):
    if "+" in tweet["created_at"]:
        s_datetime = tweet["created_at"].split(" +")[0]
    else:
        s_datetime = iso8601.parse_date(tweet["created_at"]).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    if "full_text" in tweet.keys():
        s_text = tweet["full_text"]
    else:
        s_text = tweet["text"]

    data = {"created_at": s_datetime, "text": s_text}
    return data


def clean_tweet(tweet: str, s_ticker: str) -> str:
    whitespace = re.compile(r"\s+")
    web_address = re.compile(r"(?i)http(s):\/\/[a-z0-9.~_\-\/]+")
    ticker = re.compile(fr"(?i)@{s_ticker}(?=\b)")
    user = re.compile(r"(?i)@[a-z0-9_]+")

    tweet = whitespace.sub(" ", tweet)
    tweet = web_address.sub("", tweet)
    tweet = ticker.sub(s_ticker, tweet)
    tweet = user.sub("", tweet)

    return tweet


def get_user_agent() -> str:
    user_agent_strings = [
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:86.1) Gecko/20100101 Firefox/86.1",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:86.1) Gecko/20100101 Firefox/86.1",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:82.1) Gecko/20100101 Firefox/82.1",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:83.0) Gecko/20100101 Firefox/83.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:84.0) Gecko/20100101 Firefox/84.0",
    ]

    return random.choice(user_agent_strings)


# monkey patch Pandas
def text_adjustment_init(self):
    self.ansi_regx = re.compile(r"\x1B[@-_][0-?]*[ -/]*[@-~]")
    self.encoding = get_option("display.encoding")


def text_adjustment_len(self, text):
    # return compat.strlen(self.ansi_regx.sub("", text), encoding=self.encoding)
    return len(self.ansi_regx.sub("", text))


def text_adjustment_justify(self, texts, max_len, mode="right"):
    jfunc = (
        str.ljust
        if (mode == "left")
        else str.rjust
        if (mode == "right")
        else str.center
    )
    out = []
    for s in texts:
        escapes = self.ansi_regx.findall(s)
        if len(escapes) == 2:
            out.append(
                escapes[0].strip()
                + jfunc(self.ansi_regx.sub("", s), max_len)
                + escapes[1].strip()
            )
        else:
            out.append(jfunc(s, max_len))
    return out


# pylint: disable=unused-argument
def text_adjustment_join_unicode(self, lines, sep=""):
    try:
        return sep.join(lines)
    except UnicodeDecodeError:
        # sep = compat.text_type(sep)
        return sep.join([x.decode("utf-8") if isinstance(x, str) else x for x in lines])


# pylint: disable=unused-argument
def text_adjustment_adjoin(self, space, *lists, **kwargs):
    # Add space for all but the last column:
    pads = ([space] * (len(lists) - 1)) + [0]
    max_col_len = max([len(col) for col in lists])
    new_cols = []
    for col, pad in zip(lists, pads):
        width = max([self.len(s) for s in col]) + pad
        c = self.justify(col, width, mode="left")
        # Add blank cells to end of col if needed for different col lens:
        if len(col) < max_col_len:
            c.extend([" " * width] * (max_col_len - len(col)))
        new_cols.append(c)

    rows = [self.join_unicode(row_tup) for row_tup in zip(*new_cols)]
    return self.join_unicode(rows, sep="\n")


# https://github.com/pandas-dev/pandas/issues/18066#issuecomment-522192922
def patch_pandas_text_adjustment():
    pandas.io.formats.format.TextAdjustment.__init__ = text_adjustment_init
    pandas.io.formats.format.TextAdjustment.len = text_adjustment_len
    pandas.io.formats.format.TextAdjustment.justify = text_adjustment_justify
    pandas.io.formats.format.TextAdjustment.join_unicode = text_adjustment_join_unicode
    pandas.io.formats.format.TextAdjustment.adjoin = text_adjustment_adjoin


def parse_known_args_and_warn(parser, l_args):
    parser.add_argument(
        "-h", "--help", action="store_true", dest="help", help="show this help message"
    )

    (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

    if ns_parser.help:
        parser.print_help()
        print("")
        return None

    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    return ns_parser


def price_prediction_color(val: int, last_val: int) -> str:
    if float(val) > last_val:
        color = Fore.GREEN
    else:
        color = Fore.RED
    return f"{color}{val:.2f} ${Style.RESET_ALL}"


def print_pretty_prediction(df_pred: pd.DataFrame, last_price: float):
    if gtff.USE_COLOR:
        print(f"Actual price: {Fore.YELLOW}{last_price:.2f} ${Style.RESET_ALL}\n")
        print("Prediction:")
        print(df_pred.apply(price_prediction_color, last_val=last_price).to_string())
    else:
        print(f"Actual price: {last_price:.2f} $\n")
        print("Prediction:")
        print(df_pred.to_string())


def check_ohlc(type_ohlc: str) -> str:
    if bool(re.match("^[ohlca]+$", type_ohlc)):
        return type_ohlc
    raise argparse.ArgumentTypeError("The type specified is not recognized")


def lett_to_num(word: str) -> str:
    replacements = [("o", "1"), ("h", "2"), ("l", "3"), ("c", "4"), ("a", "5")]
    for (a, b) in replacements:
        word = word.replace(a, b)
    return word


def check_sources(source: str) -> str:
    available_historical_price_sources = ["yf", "av"]
    if source in available_historical_price_sources:
        return source
    raise argparse.ArgumentTypeError(
        "This source for historical data is not available."
    )


def get_flair() -> str:
    flair = {
        "rocket": "(🚀🚀)",
        "diamond": "(💎💎)",
        "stars": "(✨)",
        "baseball": "(⚾)",
        "boat": "(⛵)",
        "phone": "(☎)",
        "mercury": "(☿)",
        "sun": "(☼)",
        "moon": "(☾)",
        "nuke": "(☢)",
        "hazard": "(☣)",
        "tunder": "(☈)",
        "king": "(♔)",
        "queen": "(♕)",
        "knight": "(♘)",
        "recycle": "(♻)",
        "scales": "(⚖)",
        "ball": "(⚽)",
        "golf": "(⛳)",
        "piece": "(☮)",
        "yy": "(☯)",
    }

    if flair.get(gtff.USE_FLAIR):
        return flair[gtff.USE_FLAIR]

    return ""
