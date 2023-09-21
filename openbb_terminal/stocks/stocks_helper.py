"""Main helper."""
__docformat__ = "numpy"
# pylint: disable=too-many-lines, unsupported-assignment-operation
# pylint: disable=no-member, too-many-branches, too-many-arguments
# pylint: disable=inconsistent-return-statements
# pylint: disable=consider-using-dict-items

import logging
import os
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional, Union

import financedatabase as fd
import numpy as np
import pandas as pd
import pytz
import yfinance as yf
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas_ta import candles
from requests.exceptions import ReadTimeout
from scipy import stats

from openbb_terminal.core.plots.plotly_helper import OpenBBFigure
from openbb_terminal.core.plots.plotly_ta.ta_class import PlotlyTA
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.helper_funcs import get_user_timezone, print_rich_table, request
from openbb_terminal.rich_config import console

# pylint: disable=unused-import
from openbb_terminal.stocks.stock_statics import (
    BALANCE_PLOT,  # noqa: F401
    BALANCE_PLOT_CHOICES,  # noqa: F401
    CANDLE_SORT,  # noqa: F401
    CASH_PLOT,  # noqa: F401
    CASH_PLOT_CHOICES,  # noqa: F401
    INCOME_PLOT,  # noqa: F401
    INCOME_PLOT_CHOICES,  # noqa: F401
    INTERVALS,  # noqa: F401
    SOURCES,  # noqa: F401
    market_coverage_suffix,
)
from openbb_terminal.stocks.stocks_model import (
    load_stock_av,
    load_stock_eodhd,
    load_stock_intrinio,
    load_stock_polygon,
    load_stock_yf,
)

from . import databento_model

logger = logging.getLogger(__name__)

exch_file_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "mappings", "Mic_Codes.csv"
)
exchange_df = pd.read_csv(exch_file_path, index_col=0, header=None)
exchange_mappings = exchange_df.squeeze("columns").to_dict()


def check_datetime(
    ck_date: Optional[Union[datetime, str]] = None, start: bool = True
) -> datetime:
    """Check if given argument is string and attempts to convert to datetime.

    Parameters
    ----------
    ck_date : Optional[Union[datetime, str]], optional
        Date to check, by default None
    start : bool, optional
        If True and string is invalid, will return 1100 days ago
        If False and string is invalid, will return today, by default True

    Returns
    -------
    datetime
        Datetime object
    """
    error_catch = (datetime.now() - timedelta(days=1100)) if start else datetime.now()
    try:
        if ck_date is None:
            return error_catch
        if isinstance(ck_date, datetime):
            return ck_date
        if isinstance(ck_date, str):
            return datetime.strptime(ck_date, "%Y-%m-%d")
    except Exception:
        console.print(
            f"Invalid date format (YYYY-MM-DD), "
            f"Using {error_catch.strftime('%Y-%m-%d')} for {ck_date}"
        )
    return error_catch


def get_holidays(
    start: Optional[Union[datetime, str]] = None,
    end: Optional[Union[datetime, str]] = None,
) -> List[datetime]:
    """Get holidays between start and end dates.

    Parameters
    ----------
    start : Optional[Union[datetime, str]], optional
        Start date, by default None
    end : Optional[Union[datetime, str]], optional
        End date, by default None
    """
    start = check_datetime(start)
    end = check_datetime(end, start=False)
    return USFederalHolidayCalendar().holidays(start=start, end=end)


def search(
    query: str = "",
    country: str = "",
    sector: str = "",
    industry_group: str = "",
    industry: str = "",
    exchange: str = "",
    exchange_country: str = "",
    all_exchanges: bool = False,
) -> pd.DataFrame:
    """Search selected query for tickers.

    Parameters
    ----------
    query : str
        The search term used to find company tickers
    country: str
        Search by country to find stocks matching the criteria
    sector : str
        Search by sector to find stocks matching the criteria
    industry_group : str
        Search by industry group to find stocks matching the criteria
    industry : str
        Search by industry to find stocks matching the criteria
    exchange: str
        Search by exchange to find stock matching the criteria
    exchange_country: str
        Search by exchange country to find stock matching the criteria
    all_exchanges: bool
        Whether to search all exchanges, without this option only the United States market is searched

    Returns
    -------
    df: pd.DataFrame
        Dataframe of search results.
        Empty Dataframe if none are found.

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.stocks.search(country="United States", exchange_country="Germany")
    """
    kwargs: Dict[str, Any] = {"exclude_exchanges": False}
    if country:
        kwargs["country"] = country.replace("_", " ").title()
    if sector:
        kwargs["sector"] = sector
    if industry:
        kwargs["industry"] = industry
    if industry_group:
        kwargs["industry_group"] = industry_group
    if exchange:
        kwargs["exchange"] = exchange
    kwargs["exclude_exchanges"] = (
        False if (exchange_country or exchange) else not all_exchanges
    )

    try:
        equities_database = fd.Equities()

        if query:
            data = equities_database.search(**kwargs, name=query)
            data = pd.concat([data, equities_database.search(**kwargs, name=query)])
            data = pd.concat(
                [data, equities_database.search(**kwargs, index=query.upper())]
            )

            data = data.drop_duplicates()
        else:
            data = equities_database.search(**kwargs)
    except ReadTimeout:
        console.print(
            "[red]Unable to retrieve company data from GitHub which limits the search"
            " capabilities. This tends to be due to access restrictions for GitHub.com,"
            " please check if you can access this website without a VPN.[/red]\n"
        )
        data = pd.DataFrame()
    except ValueError:
        console.print(
            "[red]No companies were found that match the given criteria.[/red]\n"
        )
        return pd.DataFrame()

    if data.empty:
        console.print("No companies found.\n")
        return pd.DataFrame()

    df = data[
        [
            "name",
            "country",
            "sector",
            "industry_group",
            "industry",
            "exchange",
        ]
    ]

    if exchange_country and exchange_country in market_coverage_suffix:
        suffix_tickers = [
            ticker.split(".")[1] if "." in str(ticker) else ""
            for ticker in list(df.index)
        ]
        df = df[
            [val in market_coverage_suffix[exchange_country] for val in suffix_tickers]
        ]

    exchange_suffix = {}
    for k, v in market_coverage_suffix.items():
        for x in v:
            exchange_suffix[x] = k

    df = df[["name", "country", "sector", "industry_group", "industry", "exchange"]]
    # To automate renaming columns
    df.columns = [col.replace("_", " ") for col in df.columns.tolist()]
    df = df.fillna(value=np.nan)
    df = df.iloc[df.isnull().sum(axis=1).mul(1).argsort()]

    return df.reset_index()


def get_daily_stock_candidate(
    source: str,
    symbol: str,
    int_string: str,
    start_date,
    end_date,
    monthly: bool,
    weekly: bool,
) -> pd.DataFrame:
    if source == "AlphaVantage":
        return load_stock_av(symbol, int_string, start_date, end_date)

    if source == "YahooFinance":
        return load_stock_yf(symbol, start_date, end_date, weekly, monthly)

    if source == "EODHD":
        try:
            return load_stock_eodhd(symbol, start_date, end_date, weekly, monthly)
        except KeyError:
            console.print(
                "[red]Invalid symbol for EODHD. Please check your subscription.[/red]\n"
            )
            return pd.DataFrame()

    if source == "Polygon":
        return load_stock_polygon(symbol, start_date, end_date, weekly, monthly)

    if source == "Intrinio":
        return load_stock_intrinio(symbol, start_date, end_date, weekly, monthly)

    if source == "DataBento":
        return databento_model.get_historical_stock(
            symbol, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
        )

    console.print("[red]Invalid source for stock[/red]\n")
    return pd.DataFrame()


def load(
    symbol: str,
    start_date: Optional[Union[datetime, str]] = None,
    interval: int = 1440,
    end_date: Optional[Union[datetime, str]] = None,
    prepost: bool = False,
    source: str = "YahooFinance",
    weekly: bool = False,
    monthly: bool = False,
    verbose: bool = True,
):
    """Load a symbol to perform analysis using the string above as a template.

    Optional arguments and their descriptions are listed above.

    The default source is, yFinance (https://pypi.org/project/yfinance/).
    Other sources:
            -   AlphaVantage (https://www.alphavantage.co/documentation/)
            -   Eod Historical Data (https://eodhistoricaldata.com/financial-apis/)

    Please note that certain analytical features are exclusive to the specific source.

    To load a symbol from an exchange outside of the NYSE/NASDAQ default, use yFinance as the source and
    add the corresponding exchange to the end of the symbol. i.e. `BNS.TO`.  Note this may be possible with
    other paid sources check their docs.

    BNS is a dual-listed stock, there are separate options chains and order books for each listing.
    Opportunities for arbitrage may arise from momentary pricing discrepancies between listings
    with a dynamic exchange rate as a second order opportunity in ForEx spreads.

    Find the full list of supported exchanges here:
    https://help.yahoo.com/kb/exchanges-data-providers-yahoo-finance-sln2310.html

    Certain analytical features, such as VWAP, require the ticker to be loaded as intraday
    using the `-i x` argument.  When encountering this error, simply reload the symbol using
    the interval argument. i.e. `load -t BNS -s YYYY-MM-DD -i 1 -p` loads one-minute intervals,
    including Pre/After Market data, using the default source, yFinance.

    Certain features, such as the Prediction menu, require the symbol to be loaded as daily and not intraday.

    Parameters
    ----------
    symbol: str
        Ticker to get data
    start_date: str or datetime, optional
        Start date to get data from with. - datetime or string format (YYYY-MM-DD)
    interval: int
        Interval (in minutes) to get data 1, 5, 15, 30, 60 or 1440
    end_date: str or datetime, optional
        End date to get data from with. - datetime or string format (YYYY-MM-DD)
    prepost: bool
        Pre and After hours data
    source: str
        Source of data extracted
    weekly: bool
        Flag to get weekly data
    monthly: bool
        Flag to get monthly data
    verbose: bool
        Display verbose information on what was the symbol that was loaded

    Returns
    -------
    df_stock_candidate: pd.DataFrame
        Dataframe of data
    """
    start_date = start_date or (datetime.now() - timedelta(days=1100)).strftime(
        "%Y-%m-%d"
    )
    end_date = end_date or datetime.now().strftime("%Y-%m-%d")
    start_date = check_datetime(start_date)
    end_date = check_datetime(end_date, start=False)

    int_string = "Monthly" if monthly else "Weekly" if weekly else "Daily"

    # Daily
    if int(interval) == 1440:
        df_stock_candidate = get_daily_stock_candidate(
            source, symbol, int_string, start_date, end_date, monthly, weekly
        )
        is_df = isinstance(df_stock_candidate, pd.DataFrame)
        if (is_df and df_stock_candidate.empty) or (
            not is_df and not df_stock_candidate
        ):
            return pd.DataFrame()

        df_stock_candidate.index.name = "date"
        s_start = df_stock_candidate.index[0]
        s_interval = f"{interval}min"

    else:
        if source == "AlphaVantage":
            s_start = start_date
            int_string = "Minute"
            s_interval = f"{interval}min"
            if end_date:
                end_date = (end_date + timedelta(days=1)).strftime("%Y-%m-%d")
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
            df_stock_candidate = load_stock_av(
                symbol, int_string, start_date, end_date, s_interval
            )
            s_start = df_stock_candidate.index[0]

        elif source == "YahooFinance":
            s_int = str(interval) + "m"
            s_interval = s_int + "in"

            # add 1 day to end_date to include the last day
            if end_date:
                end_date = (end_date + timedelta(days=1)).strftime("%Y-%m-%d")
            else:
                end_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

            df_stock_candidate = yf.download(
                symbol,
                start=start_date.strftime("%Y-%m-%d"),
                end=end_date,
                progress=False,
                interval=s_int,
                prepost=prepost,
                show_errors=False,
            )
            # Handle the case when start and end dates aren't explicitly set
            # TODO: This is a temporary fix, need to find a better way to handle this
            if df_stock_candidate.empty:
                d_granularity = {"1m": 6, "5m": 59, "15m": 59, "30m": 59, "60m": 729}
                s_start_dt = datetime.utcnow() - timedelta(days=d_granularity[s_int])
                s_date_start = s_start_dt.strftime("%Y-%m-%d")
                df_stock_candidate = yf.download(
                    symbol,
                    start=s_date_start
                    if s_start_dt > start_date
                    else start_date.strftime("%Y-%m-%d"),
                    progress=False,
                    interval=s_int,
                    prepost=prepost,
                )

            # Check that loading a stock was not successful
            if df_stock_candidate.empty:
                console.print("[red]No results found in yahoo finance reply.[/red]")
                return pd.DataFrame()

            df_stock_candidate.index = pd.to_datetime(
                df_stock_candidate.index
            ).tz_localize(None)

            s_start_dt = df_stock_candidate.index[0]

            s_start = (
                pytz.utc.localize(s_start_dt) if s_start_dt > start_date else start_date
            )

            df_stock_candidate.index.name = "date"

        elif source == "Intrinio":
            console.print(
                "[red]We currently do not support intraday data with Intrinio.[/red]\n"
            )
            return pd.DataFrame()

        elif source == "Polygon":
            request_url = (
                f"https://api.polygon.io/v2/aggs/ticker/"
                f"{symbol.upper()}/range/{interval}/minute/{start_date.strftime('%Y-%m-%d')}"
                f"/{end_date.strftime('%Y-%m-%d')}"
                f"?adjusted=true&sort=desc&limit=49999&apiKey={get_current_user().credentials.API_POLYGON_KEY}"
            )
            r = request(request_url)
            if r.status_code != 200:
                console.print("[red]Error in polygon request[/red]")
                return pd.DataFrame()

            r_json = r.json()
            if "results" not in r_json:
                console.print("[red]No results found in polygon reply.[/red]")
                return pd.DataFrame()

            df_stock_candidate = pd.DataFrame(r_json["results"])

            df_stock_candidate = df_stock_candidate.rename(
                columns={
                    "o": "Open",
                    "c": "Close",
                    "h": "High",
                    "l": "Low",
                    "t": "date",
                    "v": "Volume",
                    "n": "Transactions",
                }
            )
            # pylint: disable=unsupported-assignment-operation
            df_stock_candidate["date"] = pd.to_datetime(
                df_stock_candidate.date, unit="ms"
            )
            df_stock_candidate["Adj Close"] = df_stock_candidate.Close
            df_stock_candidate = df_stock_candidate.sort_values(by="date")

            df_stock_candidate = df_stock_candidate.set_index("date")
            # Check that loading a stock was not successful
            if df_stock_candidate.empty:
                return pd.DataFrame()

            df_stock_candidate.index = (
                df_stock_candidate.index.tz_localize(tz="UTC")
                .tz_convert(get_user_timezone())
                .tz_localize(None)
            )
            s_start_dt = df_stock_candidate.index[0]

            s_start = (
                pytz.utc.localize(s_start_dt) if s_start_dt > start_date else start_date
            )
            s_interval = f"{interval}min"

        elif source == "EODHD":
            df_stock_candidate = load_stock_eodhd(
                symbol, start_date, end_date, weekly, monthly, intraday=True
            )

            if df_stock_candidate.empty:
                return pd.DataFrame()

            df_stock_candidate.index = df_stock_candidate.index.tz_convert(
                get_user_timezone()
            ).tz_localize(None)

            s_start_dt = df_stock_candidate.index[0]

            s_start = (
                pytz.utc.localize(s_start_dt) if s_start_dt > start_date else start_date
            )

            s_interval = f"{interval}min"

        else:
            console.print("[red]Invalid intraday data source[/red]")
            return pd.DataFrame()

        if not prepost:
            df_stock_candidate = df_stock_candidate.between_time("9:30", "16:00")

        int_string = "Intraday"

    s_intraday = (f"Intraday {interval}min", int_string)[interval == 1440]

    if verbose:
        console.print(
            f"Loading {s_intraday} data for {symbol.upper()} "
            f"with starting period {s_start.strftime('%Y-%m-%d')}."
        )

    df_stock_candidate.name = symbol.upper()

    return df_stock_candidate


def display_candle(
    symbol: str,
    data: Optional[pd.DataFrame] = None,
    add_trend: bool = False,
    ma: Optional[Iterable[int]] = None,
    asset_type: str = "",
    start_date: Optional[Union[datetime, str]] = None,
    interval: int = 1440,
    end_date: Optional[Union[datetime, str]] = None,
    prepost: bool = False,
    source: str = "YahooFinance",
    weekly: bool = False,
    monthly: bool = False,
    ha: Optional[bool] = False,
    external_axes: bool = False,
    raw: bool = False,
    yscale: str = "linear",
) -> Union[None, OpenBBFigure]:
    """Show candle plot of loaded ticker.

    [Source: Yahoo Finance, IEX Cloud or Alpha Vantage]

    Parameters
    ----------
    symbol: str
        Ticker name
    data: pd.DataFrame
        Stock dataframe
    add_trend: bool
        Flag to add high and low trends to chart
    ma: Tuple[int]
        Moving averages to add to the candle
    asset_type: str
        String to include in title
    start_date: str or datetime, optional
        Start date to get data from with. - datetime or string format (YYYY-MM-DD)
    interval: int
        Interval (in minutes) to get data 1, 5, 15, 30, 60 or 1440
    end_date: str or datetime, optional
        End date to get data from with. - datetime or string format (YYYY-MM-DD)
    prepost: bool
        Pre and After hours data
    source: str
        Source of data extracted
    weekly: bool
        Flag to get weekly data
    monthly: bool
        Flag to get monthly data
    ha: bool
        Flag to show Heikin Ashi candles.
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    raw : bool, optional
        Flag to display raw data, by default False
    yscale: str
        Linear or log for yscale

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.stocks.candle("AAPL")
    """
    # We are not actually showing adj close in candle.  This hasn't been an issue so far, but adding
    # in intrinio returns all adjusted columns,so some care here is needed or else we end up with
    # mixing up close and adj close
    if data is None:
        # For mypy
        data = pd.DataFrame()
    data = deepcopy(data)

    if "Adj Close" in data.columns:
        data["Close"] = data["Adj Close"].copy()

    if start_date is None:
        start_date = (datetime.now() - timedelta(days=1100)).strftime("%Y-%m-%d")

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    start_date = check_datetime(start_date)
    end_date = check_datetime(end_date, start=False)

    if data is None or data.empty:
        data = load(
            symbol,
            start_date,
            interval,
            end_date,
            prepost,
            source,
            weekly,
            monthly,
        )
        data = process_candle(data)

    if add_trend and (data.index[1] - data.index[0]).total_seconds() >= 86400:
        data = find_trendline(data, "OC_High", "high")
        data = find_trendline(data, "OC_Low", "low")

    if raw:
        return data

    kwargs = {}
    if ma:
        kwargs["rma"] = dict(length=ma)

    if data.index[-2].date() == data.index[-1].date():
        interval = int((data.index[1] - data.index[0]).seconds / 60)

    data.name = f"{asset_type} {symbol}"

    if ha:
        data_ = heikin_ashi(data)
        data["Open"] = data_["HA Open"]
        data["High"] = data_["HA High"]
        data["Low"] = data_["HA Low"]
        data["Close"] = data_["HA Close"]
        data.name = f"{symbol} - Heikin Ashi Candles"

    fig = PlotlyTA.plot(data, dict(**kwargs))

    if add_trend:
        fig.add_trend(data, secondary_y=False)

    fig.update_layout(yaxis=dict(type=yscale))

    return fig.show(external=external_axes)


def process_candle(data: pd.DataFrame) -> pd.DataFrame:
    """Process DataFrame into candle style plot.

    Parameters
    ----------
    data : DataFrame
        Stock dataframe.

    Returns
    -------
    DataFrame
        A Panda's data frame with columns Open, High, Low, Close, Adj Close, Volume,
        date_id, OC-High, OC-Low.
    """
    df_data = data.copy()
    df_data["date_id"] = (df_data.index.date - df_data.index.date.min()).astype(
        "timedelta64[D]"
    )
    df_data["date_id"] = df_data["date_id"].dt.days + 1

    df_data["OC_High"] = df_data[["Open", "Close"]].max(axis=1)
    df_data["OC_Low"] = df_data[["Open", "Close"]].min(axis=1)

    return df_data


def find_trendline(
    df_data: pd.DataFrame, y_key: str, high_low: str = "high"
) -> pd.DataFrame:
    """Attempt to find a trend line based on y_key column from a given stock ticker data frame.

    Parameters
    ----------
    df_data : DataFrame
        The stock ticker data frame with at least date_id, y_key columns.
    y_key : str
        Column name to base the trend line on.
    high_low: str, optional
        Either "high" or "low". High is the default.

    Returns
    -------
    DataFrame
        If a trend is successfully found,
            An updated Panda's data frame with a trend data {y_key}_trend column.
        If no trend was found,
            An original Panda's data frame
    """
    for iteration in [3, 4, 5, 6, 7]:
        df_temp = df_data.copy()
        while len(df_temp) > iteration:
            reg = stats.linregress(x=df_temp["date_id"], y=df_temp[y_key])

            if high_low == "high":
                df_temp = df_temp.loc[
                    df_temp[y_key] > reg[0] * df_temp["date_id"] + reg[1]
                ]
            else:
                df_temp = df_temp.loc[
                    df_temp[y_key] < reg[0] * df_temp["date_id"] + reg[1]
                ]

        if len(df_temp) > 1:
            break

    if len(df_temp) == 1:
        return df_data

    reg = stats.linregress(x=df_temp["date_id"], y=df_temp[y_key])

    df_data[f"{y_key}_trend"] = reg[0] * df_data["date_id"] + reg[1]

    return df_data


def additional_info_about_ticker(ticker: str) -> str:
    """Get information about trading the ticker.

    Includes exchange, currency, timezone and market status.

    Parameters
    ----------
    ticker : str
        The stock ticker to extract if stock market is open or not
    Returns
    -------
    str
        Additional information about trading the ticker
    """
    extra_info = ""

    if ticker:
        if ".US" in ticker.upper():
            ticker = ticker.rstrip(".US")
            ticker = ticker.rstrip(".us")
        ticker_stats = yf.Ticker(ticker).stats()
        extra_info += "\n[param]Company:  [/param]"
        extra_info += ticker_stats.get("quoteType", {}).get("shortName")
        extra_info += "\n[param]Exchange: [/param]"
        exchange_name = ticker_stats.get("quoteType", {}).get("exchange")
        extra_info += (
            exchange_mappings["X" + exchange_name]
            if "X" + exchange_name in exchange_mappings
            else exchange_name
        )

        extra_info += "\n[param]Currency: [/param]"
        extra_info += ticker_stats.get("summaryDetail", {}).get("currency")

    else:
        extra_info += "\n[param]Company: [/param]"
        extra_info += "\n[param]Exchange: [/param]"
        extra_info += "\n[param]Currency: [/param]"

    return extra_info + "\n"


def clean_fraction(num, denom):
    """Return the decimal value or NA if the operation cannot be performed.

    Parameters
    ----------
    num : Any
        The numerator for the fraction
    denom : Any
        The denominator for the fraction

    Returns
    -------
    val : Any
        The value of the fraction
    """
    try:
        return num / denom
    except TypeError:
        return "N/A"


def load_custom(file_path: str) -> pd.DataFrame:
    """Load in a custom csv file.

    Parameters
    ----------
    file_path: str
        Path to file

    Returns
    -------
    pd.DataFrame
        Dataframe of stock data
    """
    # Double check that the file exists
    if not os.path.exists(file_path):
        console.print("[red]File path does not exist.[/red]\n")
        return pd.DataFrame()

    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith(".xlsx"):
        df = pd.read_excel(file_path)
    else:
        console.print("[red]File type not supported.[/red]\n")
        return pd.DataFrame()

    console.print(f"Loaded data has columns: {', '.join(df.columns.to_list())}\n")

    # Nasdaq specific
    if "Close/Last" in df.columns:
        df = df.rename(columns={"Close/Last": "Close"})
    if "Last" in df.columns:
        df = df.rename(columns={"Last": "Close"})

    df.columns = [col.lower().rstrip().lstrip() for col in df.columns]

    for col in df.columns:
        if col in ["date", "time", "timestamp", "datetime"]:
            df[col] = pd.to_datetime(df[col])
            df = df.set_index(col)
            console.print(f"Column [blue]{col.title()}[/blue] set as index.")

    df.columns = [col.title() for col in df.columns]
    df.index.name = df.index.name.title()

    df = df.applymap(
        lambda x: clean_function(x) if not isinstance(x, (int, float)) else x
    )
    if "Adj Close" not in df.columns:
        df["Adj Close"] = df.Close.copy()

    return df


def clean_function(entry: str) -> Union[str, float]:
    """Clean stock data from csv.

    This can be customized for csvs.
    """
    # If there is a digit, get rid of common characters and return float
    if any(char.isdigit() for char in entry):
        return float(entry.replace("$", "").replace(",", ""))
    return entry


def show_quick_performance(
    stock_df: pd.DataFrame,
    ticker: str,
) -> None:
    """Show quick performance stats of stock prices.

    Daily prices expected.
    """
    closes = stock_df["Adj Close"]
    volumes = stock_df["Volume"]

    perfs = {
        "1 Day": 100 * closes.pct_change(2)[-1],
        "1 Week": 100 * closes.pct_change(5)[-1],
        "1 Month": 100 * closes.pct_change(21)[-1],
        "1 Year": 100 * closes.pct_change(252)[-1],
    }

    closes_ytd = closes[closes.index.year == pd.to_datetime("today").year]
    if not closes_ytd.empty:
        perfs["YTD"] = 100 * (closes_ytd[-1] - closes_ytd[0]) / closes_ytd[0]
    else:
        perfs["Period"] = 100 * (closes[-1] - closes[0]) / closes[0]

    perf_df = pd.DataFrame.from_dict(perfs, orient="index").dropna().T
    perf_df = perf_df.applymap(lambda x: str(round(x, 2)) + " %")
    if len(closes) > 252:
        perf_df["Volatility (1Y)"] = (
            str(round(100 * np.sqrt(252) * closes[-252:].pct_change().std(), 2)) + " %"
        )
    else:
        perf_df["Volatility (Ann)"] = (
            str(round(100 * np.sqrt(252) * closes.pct_change().std(), 2)) + " %"
        )
    if len(volumes) > 10:
        perf_df["Volume (10D avg)"] = (
            str(round(np.mean(volumes[-12:-2]) / 1_000_000, 2)) + " M"
        )

    perf_df["Previous Close"] = str(round(closes[-1], 2))

    print_rich_table(
        perf_df,
        show_index=False,
        headers=perf_df.columns,
        title=f"{ticker.upper()} Performance",
    )


def show_codes_polygon(ticker: str):
    """Show FIGI, SIC and SIK codes for ticker.

    Parameters
    ----------
    ticker: str
        Stock ticker
    """

    current_user = get_current_user()

    link = (
        f"https://api.polygon.io/v3/reference/tickers/{ticker.upper()}?apiKey="
        f"{current_user.credentials.API_POLYGON_KEY}"
    )
    if current_user.credentials.API_POLYGON_KEY == "REPLACE_ME":
        console.print("[red]Polygon API key missing[/red]\n")
        return
    r = request(link)
    if r.status_code != 200:
        console.print("[red]Error in polygon request[/red]\n")
        return
    r_json = r.json()
    if "results" not in r_json:
        console.print("[red]Results not found in polygon request[/red]")
        return
    r_json = r_json["results"]
    cols = ["cik", "composite_figi", "share_class_figi", "sic_code"]
    vals = [r_json[col] for col in cols]
    polygon_df = pd.DataFrame(
        {"codes": [c.upper() for c in cols], "values": vals},
        columns=["codes", "values"],
    )
    polygon_df.codes = polygon_df.codes.apply(lambda x: x.replace("_", " "))
    print_rich_table(
        polygon_df,
        show_index=False,
        headers=["code", "value"],
        title=f"{ticker.upper()} Codes",
    )


def format_parse_choices(choices: List[str]) -> List[str]:
    """Format a list of strings to be lowercase and replace spaces with underscores.

    Parameters
    ----------
    choices: List[str]
        The options to be formatted

    Returns
    -------
    clean_choices: List[str]
        The cleaned options

    """
    return [x.lower().replace(" ", "_") for x in choices]


def map_parse_choices(choices: List[str]) -> Dict[str, str]:
    """Create a mapping of clean arguments (keys) to original arguments (values).

    Parameters
    ----------
    choices: List[str]
        The options to be formatted

    Returns
    -------
    clean_choices: Dict[str, str]
        The mapping

    """
    the_dict = {x.lower().replace(" ", "_"): x for x in choices}
    the_dict[""] = ""
    return the_dict


def verify_plot_options(command: str, source: str, plot: list) -> bool:
    """Verify that the plot options are valid for the chosen source."""
    if command == "cash":
        command_options = CASH_PLOT
    elif command == "balance":
        command_options = BALANCE_PLOT
    else:
        command_options = INCOME_PLOT
    options = list(command_options.get(source, {}).values())

    incorrect_columns = []
    for column in plot:
        if column not in options:
            incorrect_columns.append(column)
    if incorrect_columns:
        console.print(
            f"[red]The chosen columns to plot is not available for {source}.[/red]\n"
        )
        for column in incorrect_columns:
            possible_sources = []
            for i in command_options:
                if column in list(command_options[i].values()):
                    possible_sources.append(i)
            if possible_sources:
                console.print(
                    f"[red]{column} can be plotted with the following sources: {', '.join(possible_sources)}[/red]"
                )
            else:
                console.print(
                    f"[red]{column} does not exist in a existing data source.[/red]"
                )
        return True
    return False


def heikin_ashi(data: pd.DataFrame) -> pd.DataFrame:
    """Return OHLC data as Heikin Ashi Candles.

    Parameters
    ----------
    data: pd.DataFrame
        DataFrame containing OHLC data.

    Returns
    -------
    pd.DataFrame
        Appended DataFrame with Heikin Ashi candle calculations.
    """

    check_columns = ["Open", "High", "Low", "Close"]

    data.rename(
        columns={"open": "Open", "high": "High", "low": "Low", "close": "Close"},
        inplace=True,
    )

    for item in check_columns:
        if item not in data.columns:
            raise ValueError(
                "The expected column labels, "
                f"{check_columns}"
                ", were not found in DataFrame."
            )

    ha = candles.ha(
        data["Open"],
        data["High"],
        data["Low"],
        data["Close"],
    )
    ha.columns = [
        "HA Open",
        "HA High",
        "HA Low",
        "HA Close",
    ]

    return pd.concat([data, ha], axis=1)


def calculate_adjusted_prices(df: pd.DataFrame, column: str, dividends: bool = False):
    """Calculates the split-adjusted prices, or split and dividend adjusted prices.

    Parameters
    ------------
    df: pd.DataFrame
        DataFrame with unadjusted OHLCV values + Split Factor + Dividend
    column: str
        The column name to adjust.
    dividends: bool
        Whether to adjust for both splits and dividends. Default is split-adjusted only.

    Returns
    --------
    pd.DataFrame
        DataFrame with adjusted prices.
    """

    df = df.copy()
    adj_column = "Adj " + column

    # Reverse the DataFrame order, sorting by date in descending order
    df.sort_index(ascending=False, inplace=True)

    price_col = df[column].values
    split_col = df["Volume Factor"] if column == "Volume" else df["Split Factor"].values
    dividend_col = df["Dividend"].values if dividends else np.zeros(len(price_col))
    adj_price_col = np.zeros(len(df.index))
    adj_price_col[0] = price_col[0]

    for i in range(1, len(price_col)):
        adj_price_col[i] = adj_price_col[i - 1] + adj_price_col[i - 1] * (
            ((price_col[i] * split_col[i - 1]) - price_col[i - 1] - dividend_col[i - 1])
            / price_col[i - 1]
        )
    df[adj_column] = adj_price_col

    # Change the DataFrame order back to dates ascending
    df.sort_index(ascending=True, inplace=True)
    return df
