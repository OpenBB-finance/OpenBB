"""Helper functions"""
__docformat__ = "numpy"
import argparse
from typing import List
from datetime import datetime, timedelta, time as Time
import os
import random
import re
import sys
import pandas as pd
from pytz import timezone
from prettytable import PrettyTable
import iso8601
import matplotlib
import matplotlib.pyplot as plt
from holidays import US as holidaysUS
from colorama import Fore, Style
from pandas._config.config import get_option
from pandas.plotting import register_matplotlib_converters
import pandas.io.formats.format
from screeninfo import get_monitors
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal import config_plot as cfgPlot

register_matplotlib_converters()
if cfgPlot.BACKEND is not None:
    matplotlib.use(cfgPlot.BACKEND)


def check_valid_path(path: str) -> str:
    """Argparse type function to test is path is valid

    Parameters
    ----------
    path: str
        Path supplied

    Returns
    -------
    path: str
        Valid path

    Raises
    -------
    argparse.ArgumentTypeError
        Given path does not exist
    """
    if not os.path.exists(
        os.path.abspath(
            os.path.join(
                "gamestonk_terminal", "portfolio_analysis", "portfolios", f"{path}.csv"
            )
        )
    ):
        raise argparse.ArgumentTypeError("Path does not exist")
    return path


def check_int_range(mini: int, maxi: int):
    """Checks if argparse argument is an int between 2 values.

    Parameters
    ----------
    mini: int
        Min value to compare
    maxi: int
        Max value to compare

    Returns
    -------
    int_range_checker:
        Function that compares the three integers
    """

    # Define the function with default arguments
    def int_range_checker(num: int) -> int:
        """Checks if int is between a high and low value

        Parameters
        ----------
        num: int
            Input integer

        Returns
        -------
        num: int
            Input number if conditions are met

        Raises
        -------
        argparse.ArgumentTypeError
            Input number not between min and max values
        """
        num = int(num)
        if num < mini or num > maxi:
            raise argparse.ArgumentTypeError(f"must be in range [{mini},{maxi}]")
        return num

    # Return function handle to checking function
    return int_range_checker


def check_non_negative(value) -> int:
    """Argparse type to check non negative int"""
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError(f"{value} is negative")
    return ivalue


def check_positive(value) -> int:
    """Argparse type to check positive int"""
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(f"{value} is an invalid positive int value")
    return ivalue


def valid_date(s: str) -> datetime:
    """Argparse type to check date is in valid format"""
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError as value_error:
        raise argparse.ArgumentTypeError(f"Not a valid date: {s}") from value_error


def plot_view_stock(df: pd.DataFrame, symbol: str, interval: str):
    """
    Plot the loaded stock dataframe
    Parameters
    ----------
    df: Dataframe
        Dataframe of prices and volumnes
    symbol: str
        Symbol of ticker
    interval: str
        Stock data resolution for plotting purposes

    """
    df.sort_index(ascending=True, inplace=True)
    bar_colors = ["r" if x[1].Open < x[1].Close else "g" for x in df.iterrows()]

    try:
        fig, ax = plt.subplots(
            2,
            1,
            gridspec_kw={"height_ratios": [3, 1]},
            figsize=plot_autoscale(),
            dpi=cfgPlot.PLOT_DPI,
        )
    except Exception as e:
        print(e)
        print(
            "Encountered an error trying to open a chart window. Check your X server configuration."
        )
        return

    # In order to make nice Volume plot, make the bar width = interval
    if interval == "1440min":
        bar_width = timedelta(days=1)
        title_string = "Daily"
    else:
        bar_width = timedelta(minutes=int(interval.split("m")[0]))
        title_string = f"{int(interval.split('m')[0])} min"

    ax[0].yaxis.tick_right()
    if "Adj Close" in df.columns:
        ax[0].plot(df.index, df["Adj Close"], c=cfgPlot.VIEW_COLOR)
    else:
        ax[0].plot(df.index, df["Close"], c=cfgPlot.VIEW_COLOR)
    ax[0].set_xlim(df.index[0], df.index[-1])
    ax[0].set_xticks([])
    ax[0].yaxis.set_label_position("right")
    ax[0].set_ylabel("Share Price ($)")
    ax[0].grid(axis="y", color="gainsboro", linestyle="-", linewidth=0.5)

    ax[0].spines["top"].set_visible(False)
    ax[0].spines["left"].set_visible(False)
    ax[1].bar(
        df.index, df.Volume / 1_000_000, color=bar_colors, alpha=0.8, width=bar_width
    )
    ax[1].set_xlim(df.index[0], df.index[-1])
    ax[1].yaxis.tick_right()
    ax[1].yaxis.set_label_position("right")
    ax[1].set_ylabel("Volume (1M)")
    ax[1].grid(axis="y", color="gainsboro", linestyle="-", linewidth=0.5)
    ax[1].spines["top"].set_visible(False)
    ax[1].spines["left"].set_visible(False)
    ax[1].set_xlabel("Time")
    fig.suptitle(
        symbol + " " + title_string,
        size=20,
        x=0.15,
        y=0.95,
        fontfamily="serif",
        fontstyle="italic",
    )
    if gtff.USE_ION:
        plt.ion()
    fig.tight_layout(pad=2)
    plt.setp(ax[1].get_xticklabels(), rotation=20, horizontalalignment="right")

    plt.show()
    print("")


def us_market_holidays(years) -> list:
    """get US market holidays"""
    if isinstance(years, int):
        years = [
            years,
        ]
    # https://www.nyse.com/markets/hours-calendars
    marketHolidays = [
        "Martin Luther King Jr. Day",
        "Washington's Birthday",
        "Memorial Day",
        "Independence Day",
        "Labor Day",
        "Thanksgiving",
        "Christmas Day",
    ]
    #   http://www.maa.clell.de/StarDate/publ_holidays.html
    goodFridays = {
        2010: "2010-04-02",
        2011: "2011-04-22",
        2012: "2012-04-06",
        2013: "2013-03-29",
        2014: "2014-04-18",
        2015: "2015-04-03",
        2016: "2016-03-25",
        2017: "2017-04-14",
        2018: "2018-03-30",
        2019: "2019-04-19",
        2020: "2020-04-10",
        2021: "2021-04-02",
        2022: "2022-04-15",
        2023: "2023-04-07",
        2024: "2024-03-29",
        2025: "2025-04-18",
        2026: "2026-04-03",
        2027: "2027-03-26",
        2028: "2028-04-14",
        2029: "2029-03-30",
        2030: "2030-04-19",
    }
    marketHolidays_and_obsrvd = marketHolidays + [
        holiday + " (Observed)" for holiday in marketHolidays
    ]
    allHolidays = holidaysUS(years=years)
    validHolidays = []
    for date in list(allHolidays):
        if allHolidays[date] in marketHolidays_and_obsrvd:
            validHolidays.append(date)
    for year in years:
        new_Year = datetime.strptime(f"{year}-01-01", "%Y-%m-%d")
        if new_Year.weekday() != 5:  # ignore saturday
            validHolidays.append(new_Year.date())
        if new_Year.weekday() == 6:  # add monday for Sunday
            validHolidays.append(new_Year.date() + timedelta(1))
    for year in years:
        validHolidays.append(datetime.strptime(goodFridays[year], "%Y-%m-%d").date())
    return validHolidays


def b_is_stock_market_open() -> bool:
    """checks if the stock market is open"""
    # Get current US time
    now = datetime.now(timezone("US/Eastern"))
    # Check if it is a weekend
    if now.date().weekday() > 4:
        return False
    # Check if it is a holiday
    if now.strftime("%Y-%m-%d") in us_market_holidays(now.year):
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
    """gets the next stock market day. Checks against weekends and holidays"""
    n_days = 0
    l_pred_days = list()
    years: list = []
    holidays: list = []
    while n_days < n_next_days:
        last_stock_day += timedelta(hours=24)
        year = last_stock_day.date().year
        if year not in years:
            years.append(year)
            holidays = holidays + us_market_holidays(year)
        # Check if it is a weekend
        if last_stock_day.date().weekday() > 4:
            continue
        # Check if it is a holiday
        if last_stock_day.strftime("%Y-%m-%d") in holidays:
            continue
        # Otherwise stock market is open
        n_days += 1
        l_pred_days.append(last_stock_day)

    return l_pred_days


def get_data(tweet):
    """Gets twitter data from API request"""
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
    """Cleans tweets to be fed to sentiment model"""
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
    max_col_len = max(len(col) for col in lists)
    new_cols = []
    for col, pad in zip(lists, pads):
        width = max(self.len(s) for s in col) + pad
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


def parse_known_args_and_warn(parser: argparse.ArgumentParser, other_args: List[str]):
    """Parses list of arguments into the supplied parser

    Parameters
    ----------
    parser: argparse.ArgumentParser
        Parser with predefined arguments
    other_args: List[str]
        List of arguments to parse

    Returns
    -------
    ns_parser:
        Namespace with parsed arguments
    """
    parser.add_argument(
        "-h", "--help", action="store_true", help="show this help message"
    )

    if gtff.USE_CLEAR_AFTER_CMD:
        os.system("cls||clear")

    (ns_parser, l_unknown_args) = parser.parse_known_args(other_args)

    if ns_parser.help:
        parser.print_help()
        print("")
        return None

    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    return ns_parser


def financials_colored_values(val: str) -> str:
    if val == "N/A" or str(val) == "nan":
        val = f"{Fore.YELLOW}N/A{Style.RESET_ALL}"
    elif sum(c.isalpha() for c in val) < 2:
        if "%" in val:
            if "-" in val:
                val = f"{Fore.RED}{val}{Style.RESET_ALL}"
            else:
                val = f"{Fore.GREEN}{val}{Style.RESET_ALL}"
        elif "(" in val:
            val = f"{Fore.RED}{val}{Style.RESET_ALL}"

    return val


def check_ohlc(type_ohlc: str) -> str:
    """Check that data is in ohlc"""
    if bool(re.match("^[ohlca]+$", type_ohlc)):
        return type_ohlc
    raise argparse.ArgumentTypeError("The type specified is not recognized")


def lett_to_num(word: str) -> str:
    """Matches ohlca to integers"""
    replacements = [("o", "1"), ("h", "2"), ("l", "3"), ("c", "4"), ("a", "5")]
    for (a, b) in replacements:
        word = word.replace(a, b)
    return word


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


def str_to_bool(value) -> bool:
    """Match a string to a boolean value"""
    if isinstance(value, bool):
        return value
    if value.lower() in {"false", "f", "0", "no", "n"}:
        return False
    if value.lower() in {"true", "t", "1", "yes", "y"}:
        return True
    raise ValueError(f"{value} is not a valid boolean value")


def get_screeninfo():
    screens = get_monitors()  # Get all available monitors
    if len(screens) - 1 < cfgPlot.MONITOR:  # Check to see if chosen monitor is detected
        monitor = 0
        print(f"Could not locate monitor {cfgPlot.MONITOR}, using primary monitor.")
    else:
        monitor = cfgPlot.MONITOR
    main_screen = screens[monitor]  # Choose what monitor to get

    return (main_screen.width, main_screen.height)


def plot_autoscale():

    if gtff.USE_PLOT_AUTOSCALING:
        x, y = get_screeninfo()  # Get screen size
        x = ((x) * cfgPlot.PLOT_WIDTH_PERCENTAGE * 10 ** -2) / (
            cfgPlot.PLOT_DPI
        )  # Calculate width
        if cfgPlot.PLOT_HEIGHT_PERCENTAGE == 100:  # If full height
            y = y - 60  # Remove the height of window toolbar
        y = ((y) * cfgPlot.PLOT_HEIGHT_PERCENTAGE * 10 ** -2) / (cfgPlot.PLOT_DPI)
    else:  # If not autoscale, use size defined in config_plot.py
        x = cfgPlot.PLOT_WIDTH / (cfgPlot.PLOT_DPI)
        y = cfgPlot.PLOT_HEIGHT / (cfgPlot.PLOT_DPI)
    return x, y


def print_and_record_reddit_post(submissions_dict, submission):
    # Refactor data
    s_datetime = datetime.utcfromtimestamp(submission.created_utc).strftime(
        "%d/%m/%Y %H:%M:%S"
    )
    s_link = f"https://old.reddit.com{submission.permalink}"
    s_all_awards = ""
    for award in submission.all_awardings:
        s_all_awards += f"{award['count']} {award['name']}\n"
    s_all_awards = s_all_awards[:-2]
    # Create dictionary with data to construct dataframe allows to save data
    submissions_dict[submission.id] = {
        "created_utc": s_datetime,
        "subreddit": submission.subreddit,
        "link_flair_text": submission.link_flair_text,
        "title": submission.title,
        "score": submission.score,
        "link": s_link,
        "num_comments": submission.num_comments,
        "upvote_ratio": submission.upvote_ratio,
        "awards": s_all_awards,
    }
    # Print post data collected so far
    print(f"{s_datetime} - {submission.title}")
    print(f"{s_link}")
    t_post = PrettyTable(
        ["Subreddit", "Flair", "Score", "# Comments", "Upvote %", "Awards"]
    )
    t_post.add_row(
        [
            submission.subreddit,
            submission.link_flair_text,
            submission.score,
            submission.num_comments,
            f"{round(100 * submission.upvote_ratio)}%",
            s_all_awards,
        ]
    )
    print(t_post)
    print("\n")


def get_last_time_market_was_open(dt):
    # Check if it is a weekend
    if dt.date().weekday() > 4:
        dt = get_last_time_market_was_open(dt - timedelta(hours=24))

    # Check if it is a holiday
    if dt.strftime("%Y-%m-%d") in holidaysUS():
        dt = get_last_time_market_was_open(dt - timedelta(hours=24))

    dt = dt.replace(hour=21, minute=0, second=0)

    return dt


def find_tickers(submission):
    ls_text = list()
    ls_text.append(submission.selftext)
    ls_text.append(submission.title)

    submission.comments.replace_more(limit=0)
    for comment in submission.comments.list():
        ls_text.append(comment.body)

    l_tickers_found = list()
    for s_text in ls_text:
        for s_ticker in set(re.findall(r"([A-Z]{3,5} )", s_text)):
            l_tickers_found.append(s_ticker.strip())

    return l_tickers_found


def export_data(export_type: str, dir_path: str, func_name: str, df: pd.DataFrame):
    """Export data to a file.

    Parameters
    ----------
    export_type : str
        Type of export between: csv,json,xlsx,xls
    dir_path : str
        Path of directory from where this function is called
    func_name : str
        Name of the command that invokes this function
    df : pd.Dataframe
        Datframe containing the data
    """
    if export_type:
        export_dir = dir_path.replace("gamestonk_terminal", "exports")

        now = datetime.now()
        full_path = os.path.abspath(
            os.path.join(
                export_dir,
                f"{func_name}_{now.strftime('%Y%m%d_%H%M%S')}.{export_type}",
            )
        )

        if export_type == "csv":
            df.to_csv(full_path)
        elif export_type == "json":
            df.to_json(full_path)
        elif export_type in "xlsx":
            df.to_excel(full_path, index=True, header=True)
        else:
            print("Wrong export file specified.\n")

        print(f"Saved file: {full_path}\n")
