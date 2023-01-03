"""Main helper."""
__docformat__ = "numpy"

# pylint: disable=unsupported-assignment-operation,too-many-lines
# pylint: disable=no-member,too-many-branches,too-many-arguments
# pylint: disable=inconsistent-return-statements

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Union, Optional, Iterable, List, Dict

import financedatabase as fd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import LogLocator, ScalarFormatter
import mplfinance as mpf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytz
import requests
from requests.exceptions import ReadTimeout

import yfinance as yf
from plotly.subplots import make_subplots
from scipy import stats

from openbb_terminal import config_terminal as cfg

# pylint: disable=unused-import
from openbb_terminal.stocks.stock_statics import market_coverage_suffix
from openbb_terminal.stocks.stock_statics import INTERVALS  # noqa: F401
from openbb_terminal.stocks.stock_statics import SOURCES  # noqa: F401
from openbb_terminal.stocks.stock_statics import INCOME_PLOT  # noqa: F401
from openbb_terminal.stocks.stock_statics import BALANCE_PLOT  # noqa: F401
from openbb_terminal.stocks.stock_statics import CASH_PLOT  # noqa: F401
from openbb_terminal.stocks.stock_statics import CANDLE_SORT  # noqa: F401
from openbb_terminal.stocks.stocks_model import (
    load_stock_av,
    load_stock_yf,
    load_stock_eodhd,
    load_stock_iex_cloud,
    load_stock_polygon,
)
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
    lambda_long_number_format_y_axis,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


exch_file_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "mappings", "Mic_Codes.csv"
)
exchange_df = pd.read_csv(exch_file_path, index_col=0, header=None)
exchange_mappings = exchange_df.squeeze("columns").to_dict()


def check_datetime(
    ck_date: Optional[Union[datetime, str]] = None, start: bool = True
) -> datetime:
    """Checks if given argument is string and attempts to convert to datetime.

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


def search(
    query: str = "",
    country: str = "",
    sector: str = "",
    industry: str = "",
    exchange_country: str = "",
    limit: int = 0,
    export: str = "",
) -> None:
    """Search selected query for tickers.

    Parameters
    ----------
    query : str
        The search term used to find company tickers
    country: str
        Search by country to find stocks matching the criteria
    sector : str
        Search by sector to find stocks matching the criteria
    industry : str
        Search by industry to find stocks matching the criteria
    exchange_country: str
        Search by exchange country to find stock matching
    limit : int
        The limit of companies shown.
    export : str
        Export data

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.stocks.search(country="united states", exchange_country="Germany")
    """
    kwargs: Dict[str, Any] = {"exclude_exchanges": False}
    if country:
        kwargs["country"] = country.replace("_", " ").title()
    if sector:
        kwargs["sector"] = sector
    if industry:
        kwargs["industry"] = industry

    try:
        data = fd.select_equities(**kwargs)
    except ReadTimeout:
        console.print(
            "[red]Unable to retrieve company data from GitHub which limits the search"
            " capabilities. This tends to be due to access restrictions for GitHub.com,"
            " please check if you can access this website without a VPN.[/red]\n"
        )
        data = {}
    except ValueError:
        console.print(
            "[red]No companies were found that match the given criteria.[/red]\n"
        )
        return
    if not data:
        console.print("No companies found.\n")
        return

    if query:
        d = fd.search_products(
            data, query, search="long_name", case_sensitive=False, new_database=None
        )
    else:
        d = data

    if not d:
        console.print("No companies found.\n")
        return

    df = pd.DataFrame.from_dict(d).T[["long_name", "country", "sector", "industry"]]
    if exchange_country:
        if exchange_country in market_coverage_suffix:
            suffix_tickers = [
                ticker.split(".")[1] if "." in ticker else ""
                for ticker in list(df.index)
            ]
            df = df[
                [
                    val in market_coverage_suffix[exchange_country]
                    for val in suffix_tickers
                ]
            ]

    exchange_suffix = {}
    for k, v in market_coverage_suffix.items():
        for x in v:
            exchange_suffix[x] = k

    df["exchange"] = [
        exchange_suffix.get(ticker.split(".")[1]) if "." in ticker else "USA"
        for ticker in list(df.index)
    ]

    title = "Companies found"
    if query:
        title += f" on term {query}"
    if exchange_country:
        title += f" on an exchange in {exchange_country.replace('_', ' ').title()}"
    if country:
        title += f" in {country.replace('_', ' ').title()}"
    if sector:
        title += f" within {sector}"
        if industry:
            title += f" and {industry}"
    if not sector and industry:
        title += f" within {industry}"

    df["exchange"] = df["exchange"].apply(
        lambda x: x.replace("_", " ").title() if x else None
    )
    df["exchange"] = df["exchange"].apply(
        lambda x: "United States" if x == "Usa" else None
    )

    print_rich_table(
        df.iloc[:limit] if limit else df,
        show_index=True,
        headers=["Name", "Country", "Sector", "Industry", "Exchange"],
        title=title,
    )

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "search", df)


def load(
    symbol: str,
    start_date: Optional[Union[datetime, str]] = None,
    interval: int = 1440,
    end_date: Optional[Union[datetime, str]] = None,
    prepost: bool = False,
    source: str = "YahooFinance",
    iexrange: str = "ytd",
    weekly: bool = False,
    monthly: bool = False,
    verbose: bool = True,
):
    """Load a symbol to perform analysis using the string above as a template.

    Optional arguments and their descriptions are listed above.

    The default source is, yFinance (https://pypi.org/project/yfinance/).
    Other sources:
            -   AlphaVantage (https://www.alphavantage.co/documentation/)
            -   IEX Cloud (https://iexcloud.io/docs/api/)
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
    iexrange: str
        Timeframe to get IEX data.
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

    if start_date is None:
        start_date = (datetime.now() - timedelta(days=1100)).strftime("%Y-%m-%d")

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    start_date = check_datetime(start_date)
    end_date = check_datetime(end_date, start=False)

    # Daily
    if int(interval) == 1440:

        int_string = "Daily"
        if weekly:
            int_string = "Weekly"
        if monthly:
            int_string = "Monthly"

        if source == "AlphaVantage":
            df_stock_candidate = load_stock_av(symbol, start_date, end_date)

        elif source == "YahooFinance":
            df_stock_candidate = load_stock_yf(
                symbol, start_date, end_date, weekly, monthly
            )

        elif source == "EODHD":
            df_stock_candidate = load_stock_eodhd(
                symbol, start_date, end_date, weekly, monthly
            )

        elif source == "IEXCloud":
            df_stock_candidate = load_stock_iex_cloud(symbol, iexrange)

        elif source == "Polygon":
            df_stock_candidate = load_stock_polygon(
                symbol, start_date, end_date, weekly, monthly
            )
        else:
            console.print("[red]Invalid source for stock[/red]\n")
            return
        if df_stock_candidate.empty:
            return df_stock_candidate

        df_stock_candidate.index.name = "date"
        s_start = df_stock_candidate.index[0]
        s_interval = f"{interval}min"
        int_string = "Daily" if interval == 1440 else "Intraday"

    else:

        if source == "YahooFinance":
            s_int = str(interval) + "m"
            s_interval = s_int + "in"
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
                return pd.DataFrame()

            df_stock_candidate.index = df_stock_candidate.index.tz_localize(None)

            if s_start_dt > start_date:
                s_start = pytz.utc.localize(s_start_dt)
            else:
                s_start = start_date

            df_stock_candidate.index.name = "date"

        elif source == "Polygon":
            request_url = (
                f"https://api.polygon.io/v2/aggs/ticker/"
                f"{symbol.upper()}/range/{interval}/minute/{start_date.strftime('%Y-%m-%d')}"
                f"/{end_date.strftime('%Y-%m-%d')}"
                f"?adjusted=true&sort=desc&limit=49999&apiKey={cfg.API_POLYGON_KEY}"
            )
            r = requests.get(request_url)
            if r.status_code != 200:
                console.print("[red]Error in polygon request[/red]")
                return pd.DataFrame()

            r_json = r.json()
            if "results" not in r_json.keys():
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
                .tz_convert("US/Eastern")
                .tz_localize(None)
            )
            s_start_dt = df_stock_candidate.index[0]

            if s_start_dt > start_date:
                s_start = pytz.utc.localize(s_start_dt)
            else:
                s_start = start_date
            s_interval = f"{interval}min"
        int_string = "Intraday"

    s_intraday = (f"Intraday {s_interval}", int_string)[interval == 1440]

    if verbose:
        console.print(
            f"Loading {s_intraday} data for {symbol.upper()} "
            f"with starting period {s_start.strftime('%Y-%m-%d')}.",
        )

    return df_stock_candidate


def display_candle(
    symbol: str,
    data: pd.DataFrame = None,
    use_matplotlib: bool = True,
    intraday: bool = False,
    add_trend: bool = False,
    ma: Optional[Iterable[int]] = None,
    asset_type: str = "",
    start_date: Optional[Union[datetime, str]] = None,
    interval: int = 1440,
    end_date: Optional[Union[datetime, str]] = None,
    prepost: bool = False,
    source: str = "YahooFinance",
    iexrange: str = "ytd",
    weekly: bool = False,
    monthly: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
    raw: bool = False,
    yscale: str = "linear",
):
    """Show candle plot of loaded ticker.

    [Source: Yahoo Finance, IEX Cloud or Alpha Vantage]

    Parameters
    ----------
    symbol: str
        Ticker name
    data: pd.DataFrame
        Stock dataframe
    use_matplotlib: bool
        Flag to use matplotlib instead of interactive plotly chart
    intraday: bool
        Flag for intraday data for plotly range breaks
    add_trend: bool
        Flag to add high and low trends to chart
    ma: Tuple[int]
        Moving averages to add to the candle
    asset_type_: str
        String to include in title
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    asset_type_: str
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
    iexrange: str
        Timeframe to get IEX data.
    weekly: bool
        Flag to get weekly data
    monthly: bool
        Flag to get monthly data
    raw : bool, optional
        Flag to display raw data, by default False
    yscale: str
        Linear or log for yscale

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.stocks.candle("AAPL")
    """

    if start_date is None:
        start_date = (datetime.now() - timedelta(days=1100)).strftime("%Y-%m-%d")

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    start_date = check_datetime(start_date)
    end_date = check_datetime(end_date, start=False)

    if data is None:
        data = load(
            symbol,
            start_date,
            interval,
            end_date,
            prepost,
            source,
            iexrange,
            weekly,
            monthly,
        )
        data = process_candle(data)

    if add_trend:
        if (data.index[1] - data.index[0]).total_seconds() >= 86400:
            data = find_trendline(data, "OC_High", "high")
            data = find_trendline(data, "OC_Low", "low")

    if not raw:
        if use_matplotlib:
            ap0 = []
            if add_trend:
                if "OC_High_trend" in data.columns:
                    ap0.append(
                        mpf.make_addplot(
                            data["OC_High_trend"],
                            color=cfg.theme.up_color,
                            secondary_y=False,
                        ),
                    )

                if "OC_Low_trend" in data.columns:
                    ap0.append(
                        mpf.make_addplot(
                            data["OC_Low_trend"],
                            color=cfg.theme.down_color,
                            secondary_y=False,
                        ),
                    )

            candle_chart_kwargs = {
                "type": "candle",
                "style": cfg.theme.mpf_style,
                "volume": True,
                "addplot": ap0,
                "xrotation": cfg.theme.xticks_rotation,
                "scale_padding": {"left": 0.3, "right": 1, "top": 0.8, "bottom": 0.8},
                "update_width_config": {
                    "candle_linewidth": 0.6,
                    "candle_width": 0.8,
                    "volume_linewidth": 0.8,
                    "volume_width": 0.8,
                },
                "warn_too_much_data": 10000,
                "yscale": yscale,
            }

            kwargs = {"mav": ma} if ma else {}

            if external_axes is None:
                candle_chart_kwargs["returnfig"] = True
                candle_chart_kwargs["figratio"] = (10, 7)
                candle_chart_kwargs["figscale"] = 1.10
                candle_chart_kwargs["figsize"] = plot_autoscale()
                candle_chart_kwargs["warn_too_much_data"] = 100_000

                fig, ax = mpf.plot(data, **candle_chart_kwargs, **kwargs)
                lambda_long_number_format_y_axis(data, "Volume", ax)

                fig.suptitle(
                    f"{asset_type} {symbol}",
                    x=0.055,
                    y=0.965,
                    horizontalalignment="left",
                )

                if ma:
                    # Manually construct the chart legend
                    colors = [cfg.theme.get_colors()[i] for i, _ in enumerate(ma)]
                    lines = [Line2D([0], [0], color=c) for c in colors]
                    labels = ["MA " + str(label) for label in ma]
                    ax[0].legend(lines, labels)

                if yscale == "log":
                    ax[0].yaxis.set_major_formatter(ScalarFormatter())
                    ax[0].yaxis.set_major_locator(
                        LogLocator(base=100, subs=[1.0, 2.0, 5.0, 10.0])
                    )
                    ax[0].ticklabel_format(style="plain", axis="y")

                cfg.theme.visualize_output(force_tight_layout=False)
            else:
                if len(external_axes) != 2:
                    logger.error("Expected list of one axis item.")
                    console.print("[red]Expected list of 2 axis items.\n[/red]")
                    return pd.DataFrame()
                ax1, ax2 = external_axes
                candle_chart_kwargs["ax"] = ax1
                candle_chart_kwargs["volume"] = ax2
                mpf.plot(data, **candle_chart_kwargs)

        else:
            fig = make_subplots(
                rows=2,
                cols=1,
                shared_xaxes=True,
                vertical_spacing=0.06,
                subplot_titles=(f"{symbol}", "Volume"),
                row_width=[0.2, 0.7],
            )
            fig.add_trace(
                go.Candlestick(
                    x=data.index,
                    open=data.Open,
                    high=data.High,
                    low=data.Low,
                    close=data.Close,
                    name="OHLC",
                ),
                row=1,
                col=1,
            )
            if ma:
                plotly_colors = [
                    "black",
                    "teal",
                    "blue",
                    "purple",
                    "orange",
                    "gray",
                    "deepskyblue",
                ]
                for idx, ma_val in enumerate(ma):
                    temp = data["Adj Close"].copy()
                    temp[f"ma{ma_val}"] = data["Adj Close"].rolling(ma_val).mean()
                    temp = temp.dropna()
                    fig.add_trace(
                        go.Scatter(
                            x=temp.index,
                            y=temp[f"ma{ma_val}"],
                            name=f"MA{ma_val}",
                            mode="lines",
                            line=go.scatter.Line(
                                color=plotly_colors[np.mod(idx, len(plotly_colors))]
                            ),
                        ),
                        row=1,
                        col=1,
                    )

            if add_trend:
                if "OC_High_trend" in data.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=data.index,
                            y=data["OC_High_trend"],
                            name="High Trend",
                            mode="lines",
                            line=go.scatter.Line(color="green"),
                        ),
                        row=1,
                        col=1,
                    )
                if "OC_Low_trend" in data.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=data.index,
                            y=data["OC_Low_trend"],
                            name="Low Trend",
                            mode="lines",
                            line=go.scatter.Line(color="red"),
                        ),
                        row=1,
                        col=1,
                    )

            colors = [
                "red" if row.Open < row["Adj Close"] else "green"
                for _, row in data.iterrows()
            ]
            fig.add_trace(
                go.Bar(
                    x=data.index,
                    y=data.Volume,
                    name="Volume",
                    marker_color=colors,
                ),
                row=2,
                col=1,
            )
            fig.update_layout(
                yaxis_title="Stock Price ($)",
                xaxis=dict(
                    rangeselector=dict(
                        buttons=list(
                            [
                                dict(
                                    count=1,
                                    label="1m",
                                    step="month",
                                    stepmode="backward",
                                ),
                                dict(
                                    count=3,
                                    label="3m",
                                    step="month",
                                    stepmode="backward",
                                ),
                                dict(
                                    count=1, label="YTD", step="year", stepmode="todate"
                                ),
                                dict(
                                    count=1,
                                    label="1y",
                                    step="year",
                                    stepmode="backward",
                                ),
                                dict(step="all"),
                            ]
                        )
                    ),
                    rangeslider=dict(visible=False),
                    type="date",
                ),
            )

            fig.update_layout(
                updatemenus=[
                    dict(
                        buttons=[
                            dict(
                                label="linear",
                                method="relayout",
                                args=[{"yaxis.type": "linear"}],
                            ),
                            dict(
                                label="log",
                                method="relayout",
                                args=[{"yaxis.type": "log"}],
                            ),
                        ]
                    )
                ]
            )

            if intraday:
                fig.update_xaxes(
                    rangebreaks=[
                        dict(bounds=["sat", "mon"]),
                        dict(bounds=[20, 9], pattern="hour"),
                    ]
                )

            fig.show(config=dict({"scrollZoom": True}))
    else:
        return data


def load_ticker(
    ticker: str,
    start_date: Union[str, datetime],
    end_date: Optional[Union[str, datetime]] = None,
) -> pd.DataFrame:
    """Load a ticker data from Yahoo Finance.

    Adds a data index column data_id and Open-Close High/Low columns after loading.

    Parameters
    ----------
    ticker : str
        The stock ticker.
    start_date : Union[str,datetime]
        Start date to load stock ticker data formatted YYYY-MM-DD.
    end_date : Union[str,datetime]
        End date to load stock ticker data formatted YYYY-MM-DD.

    Returns
    -------
    DataFrame
        A Panda's data frame with columns Open, High, Low, Close, Adj Close, Volume,
        date_id, OC-High, OC-Low.

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> msft_df = openbb.stocks.load("MSFT")
    """
    df_data = yf.download(ticker, start=start_date, end=end_date, progress=False)

    df_data.index = pd.to_datetime(df_data.index)
    df_data["date_id"] = (df_data.index.date - df_data.index.date.min()).astype(
        "timedelta64[D]"
    )
    df_data["date_id"] = df_data["date_id"].dt.days + 1

    df_data["OC_High"] = df_data[["Open", "Close"]].max(axis=1)
    df_data["OC_Low"] = df_data[["Open", "Close"]].min(axis=1)

    return df_data


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

    df_data["ma20"] = df_data["Close"].rolling(20).mean().fillna(method="bfill")
    df_data["ma50"] = df_data["Close"].rolling(50).mean().fillna(method="bfill")

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
            reg = stats.linregress(
                x=df_temp["date_id"],
                y=df_temp[y_key],
            )

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

    reg = stats.linregress(
        x=df_temp["date_id"],
        y=df_temp[y_key],
    )

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

    df = pd.read_csv(file_path)
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


def show_quick_performance(stock_df: pd.DataFrame, ticker: str):
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
    perf_df = perf_df.applymap(
        lambda x: f"[red]{x}[/red]" if "-" in x else f"[green]{x}[/green]"
    )
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

    perf_df["Last Price"] = str(round(closes[-1], 2))
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
    link = f"https://api.polygon.io/v3/reference/tickers/{ticker.upper()}?apiKey={cfg.API_POLYGON_KEY}"
    if cfg.API_POLYGON_KEY == "REPLACE_ME":
        console.print("[red]Polygon API key missing[/red]\n")
        return
    r = requests.get(link)
    if r.status_code != 200:
        console.print("[red]Error in polygon request[/red]\n")
        return
    r_json = r.json()
    if "results" not in r_json.keys():
        console.print("[red]Results not found in polygon request[/red]")
        return
    r_json = r_json["results"]
    cols = ["cik", "composite_figi", "share_class_figi", "sic_code"]
    vals = [r_json[col] for col in cols]
    polygon_df = pd.DataFrame({"codes": [c.upper() for c in cols], "vals": vals})
    polygon_df.codes = polygon_df.codes.apply(lambda x: x.replace("_", " "))
    print_rich_table(
        polygon_df, show_index=False, headers=["", ""], title=f"{ticker.upper()} Codes"
    )


def format_parse_choices(choices: List[str]) -> List[str]:
    """Formats a list of strings to be lowercase and replace spaces with underscores.

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
    """Creates a mapping of clean arguments (keys) to original arguments (values)

    Parameters
    ----------
    choices: List[str]
        The options to be formatted

    Returns
    -------
    clean_choices: Dict[str, str]
        The mappung

    """
    the_dict = {x.lower().replace(" ", "_"): x for x in choices}
    the_dict[""] = ""
    return the_dict
