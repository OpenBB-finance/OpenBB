import textwrap
from datetime import datetime, timedelta

import finnhub
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytz
import requests
import yfinance as yf
from binance.client import Client
from plotly.subplots import make_subplots
from scipy import stats

from bots import imps

futures = "=F" or "^"
crypto = "-"
est_tz = pytz.timezone("America/New_York")


def dt_utcnow_local_tz():
    """Returns utcnow datetime as eastern timezone"""
    output = datetime.utcnow().astimezone(est_tz)
    return output


def heikin_ashi(df):
    """Attempts to calaculate heikin ashi based on given stock ticker data frame."""

    HA_df = df.copy()

    # Close column
    HA_df["Close"] = round(((df["Open"] + df["High"] + df["Low"] + df["Close"]) / 4), 2)

    # Open column
    for i in range(len(df)):
        if i == 0:
            HA_df.iat[0, 0] = round(((df["Open"].iloc[0] + df["Close"].iloc[0]) / 2), 2)
        else:
            HA_df.iat[i, 0] = round(
                ((HA_df.iat[i - 1, 0] + HA_df.iat[i - 1, 3]) / 2), 2
            )

    # High and Low column
    HA_df["High"] = HA_df.loc[:, ["Open", "Close"]].join(df["High"]).max(axis=1)
    HA_df["Low"] = HA_df.loc[:, ["Open", "Close"]].join(df["Low"]).min(axis=1)

    return HA_df


def find_trendline(
    df_data: pd.DataFrame, y_key: str, high_low: str = "high"
) -> pd.DataFrame:
    """Attempts to find a trend line based on y_key column from a given stock ticker data frame.

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


def stock_data(
    ticker: str = "",
    interval: int = 15,
    past_days: int = 0,
    extended_hours: bool = False,
    start="",
    end="",
    news: bool = False,
    heikin_candles: bool = False,
):
    """Grabs OHLC data . [Source: Yahoo Finance or Binance API]

    Parameters
    ----------
    ticker : Stock Ticker
    interval : Chart Minute Interval, 1440 for Daily
    past_days: Past Days to Display. Default: 0(Not for Daily)
    extended_hours: Display Pre/After Market Hours. Default: False
    start: YYYY-MM-DD format
    end: YYYY-MM-DD format
    news: Display clickable news markers on interactive chart. Default: False
    heikin_candles: Heikin Ashi candles. Default: False
    """
    if news:
        past_days = 30

    # Set max days of data due to api limits
    day_list = {
        1: 3,
        5: 57,
        15: 57,
        30: 57,
        60: 727,
        1440: past_days,
    }
    max_days = day_list[interval]

    if dt_utcnow_local_tz().weekday() not in range(2, 5):
        past_days += 3
    p_days = (
        ((past_days + 1) if (past_days < max_days) else max_days)
        if (interval != 1440 and past_days < 365)
        else 365
    )

    if start == "":
        start = dt_utcnow_local_tz() - timedelta(days=365)
        bar_start = dt_utcnow_local_tz() - timedelta(days=p_days)
        start = (
            bar_start if (bar_start < start) else start
        )  # Check if past days requested further back than start
    else:
        start = datetime.strptime(start, imps.DATE_FORMAT).astimezone(est_tz)
        bar_start = start - timedelta(days=p_days)
    if end == "":
        end = dt_utcnow_local_tz()
    else:
        end = datetime.strptime(end, imps.DATE_FORMAT).astimezone(est_tz)

    if interval == 1440 and crypto not in ticker.upper():
        df_stock = yf.download(
            ticker,
            start=start,
            end=end,
            progress=False,
        )
        df_stock = df_stock.fillna(0)

        # Check if loading a stock was not successful
        if df_stock.empty:
            raise Exception(f"No data found for {ticker.upper()}")

        df_stock.index = pd.to_datetime(df_stock.index, utc=True).tz_convert(est_tz)

        df_stock["date_id"] = (df_stock.index.date - df_stock.index.date.min()).astype(
            "timedelta64[D]"
        )
        df_stock["date_id"] = df_stock["date_id"].dt.days + 1

        df_stock["OC_High"] = df_stock[["Open", "Close"]].max(axis=1)
        df_stock["OC_Low"] = df_stock[["Open", "Close"]].min(axis=1)
    else:
        # Add days for ta processing and check if more than api limit
        past_days = (
            (past_days + 10) if (((10 + past_days) + max_days) < max_days) else max_days
        )
        s_int = str(interval) + "m"
        if crypto in ticker.upper() and (imps.API_BINANCE_KEY != "REPLACE_ME"):
            client = Client(imps.API_BINANCE_KEY, imps.API_BINANCE_SECRET)
            interval_map = {
                "1440m": client.KLINE_INTERVAL_1DAY,
                "60m": client.KLINE_INTERVAL_1HOUR,
                "1m": client.KLINE_INTERVAL_1MINUTE,
                "5m": client.KLINE_INTERVAL_5MINUTE,
                "15m": client.KLINE_INTERVAL_15MINUTE,
                "30m": client.KLINE_INTERVAL_30MINUTE,
            }

            candles = client.get_klines(
                symbol=ticker.upper().replace("-USD", "USDT"),
                interval=interval_map[s_int],
            )

            df_stock = pd.DataFrame(candles).astype(float).iloc[:, :6]
            df_stock.columns = [
                "date",
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
            ]
            if df_stock.empty:
                raise Exception(f"No data found for {ticker.upper()}.")
            df_stock = df_stock.dropna()
            df_stock = df_stock.astype(float).iloc[:, :6]
            df_stock = df_stock.set_index(
                pd.to_datetime(df_stock["date"], unit="ms", utc=True)
            ).drop("date", axis=1)

            df_stock["Adj Close"] = df_stock["Close"].copy()  # For Technical Analysis
        else:
            d_granularity = {
                "1m": past_days,
                "5m": past_days,
                "15m": past_days,
                "30m": past_days,
                "60m": past_days,
            }
            s_start_dt = dt_utcnow_local_tz() - timedelta(days=d_granularity[s_int])
            s_date_start = s_start_dt.strftime("%Y-%m-%d")
            df_stock = yf.download(
                ticker,
                start=s_date_start
                if s_start_dt > start
                else start.strftime("%Y-%m-%d"),
                progress=False,
                interval=s_int,
                prepost=extended_hours,
            )
            df_stock = df_stock.dropna()

    if heikin_candles:
        df_stock = heikin_ashi(df_stock)

    # Check if loading a stock was not successful
    if df_stock.empty:
        raise Exception(f"No data found for {ticker.upper()}.")

    df_stock.index.name = "date"

    if (df_stock.index[1] - df_stock.index[0]).total_seconds() >= 86400:
        df_stock = find_trendline(df_stock, "OC_High", "high")
        df_stock = find_trendline(df_stock, "OC_Low", "low")

    return df_stock, start, end, bar_start


# pylint: disable=R0912
def candle_fig(
    df_stock: pd.DataFrame,
    ticker: str,
    interval: int,
    extended_hours: bool = False,
    news: bool = False,
    **data,
):
    """Plot plotly candle fig with df_stock data

    Parameters
    ----------
    df_stock: OHLC Stock data
    ticker: Stock ticker
    interval: Candle minute interval
    extended_hours: Whether to plot extended hours. Defaults to False.
    news: Display clickable news markers on interactive chart. Default: False
    """
    if "rows" in data:
        fig = make_subplots(
            rows=data["rows"],
            cols=data["cols"],
            shared_xaxes=True,
            vertical_spacing=data["vertical_spacing"],
            row_width=data["row_width"],
            specs=data["specs"],
        )
    else:
        fig = make_subplots(
            rows=1,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.09,
            row_width=[1],
            specs=[[{"secondary_y": True}]],
        )
    if "bar" in data:
        dt = {1: 1, 5: 4, 15: 8, 30: 5, 60: 6, 1440: 30}
        bar_opacity = (
            0.2
            if (
                data["bar"]
                > (dt_utcnow_local_tz() - timedelta(days=dt[data["int_bar"]]))
            )
            else 0.3
        )
        bar_opacity = (
            bar_opacity
            if (
                data["bar"]
                > (dt_utcnow_local_tz() - timedelta(days=(dt[data["int_bar"]] * 3)))
            )
            else 0.33
        )
        bar_opacity = (
            bar_opacity
            if (
                data["bar"]
                > (dt_utcnow_local_tz() - timedelta(days=(dt[data["int_bar"]] * 4)))
            )
            else 0.35
        )
        bar_opacity = (
            bar_opacity
            if (
                data["bar"]
                > (dt_utcnow_local_tz() - timedelta(days=(dt[data["int_bar"]] * 10)))
            )
            else 0.4
        )
    else:
        bar_opacity = 0.2

    fig.add_trace(
        go.Candlestick(
            x=df_stock.index,
            open=df_stock.Open,
            high=df_stock.High,
            low=df_stock.Low,
            close=df_stock.Close,
            name="OHLC",
            increasing_line_color="#00ACFF",
            decreasing_line_color="#e4003a",
            showlegend=False,
        ),
        row=1,
        col=1,
        secondary_y=True,
    )
    if "OC_High_trend" in df_stock.columns:
        fig.add_trace(
            go.Scatter(
                x=df_stock.index,
                y=df_stock["OC_High_trend"],
                name="High Trend",
                mode="lines",
                line=go.scatter.Line(color="#00ACFF"),
            ),
            secondary_y=True,
            row=1,
            col=1,
        )
    if "OC_Low_trend" in df_stock.columns:
        fig.add_trace(
            go.Scatter(
                x=df_stock.index,
                y=df_stock["OC_Low_trend"],
                name="Low Trend",
                mode="lines",
                line=go.scatter.Line(color="#e4003a"),
            ),
            secondary_y=True,
            row=1,
            col=1,
        )
    fig.add_trace(
        go.Bar(
            x=df_stock.index,
            y=df_stock.Volume,
            name="Volume",
            yaxis="y2",
            marker_color="#fdc708",
            opacity=bar_opacity,
            showlegend=False,
        ),
        secondary_y=False,
        row=1,
        col=1,
    )

    # News Markers
    if news:

        df_date, df_title, df_current, df_content, df_url = [], [], [], [], []

        if (imps.API_NEWS_TOKEN != "REPLACE_ME") and crypto in ticker.upper():
            d_stock = yf.Ticker(ticker).info
            s_from = (dt_utcnow_local_tz() - timedelta(days=28)).strftime("%Y-%m-%d")
            term = (
                d_stock["shortName"].replace(" ", "+")
                if "shortName" in d_stock
                else ticker
            )

            link = (
                f"https://newsapi.org/v2/everything?q={term}&from={s_from}&sortBy=publishedAt&language=en"
                f"&apiKey={imps.API_NEWS_TOKEN}"
            )
            response = requests.get(link)
            articles = response.json()["articles"]

            for article in articles:
                dt_at = article["publishedAt"].replace("T", " ").replace("Z", "-05:00")
                df_date.append(
                    f"{datetime.strptime(dt_at, '%Y-%m-%d %H:%M:%S%z').astimezone(est_tz)}"
                )
                df_title.append(article["title"])
                grab_price = df_stock.iloc[
                    df_stock.index.get_loc(dt_at, method="nearest")
                ]
                df_current.append(grab_price.Close + 1)
                content = textwrap.fill(article["content"], 40)
                df_content.append(textwrap.indent(text=content, prefix="<br>"))
                df_url.append(article["url"])

        elif imps.API_FINNHUB_KEY != "REPLACE_ME":
            finnhub_client = finnhub.Client(api_key=imps.API_FINNHUB_KEY)
            start_new = (dt_utcnow_local_tz() - timedelta(days=30)).strftime(
                imps.DATE_FORMAT
            )
            end_new = dt_utcnow_local_tz().strftime(imps.DATE_FORMAT)
            articles = finnhub_client.company_news(
                ticker.upper(), _from=start_new, to=end_new
            )

            # Grab Data
            area_int = 0
            for article in articles:
                dt_df = datetime.fromtimestamp(article["datetime"], tz=est_tz).strftime(
                    "%Y-%m-%d %H:%M:%S%z"
                )
                df_date.append(dt_df)
                df_title.append(
                    textwrap.indent(
                        text=(textwrap.fill(article["headline"], 50)), prefix="<br>"
                    )
                )
                stock_df = df_stock.iloc[
                    df_stock.index.get_loc(dt_df, method="nearest")
                ]
                if area_int == 0:
                    df_current.append(stock_df.Close + (stock_df.Close / 80))
                    area_int += 1
                else:
                    df_current.append(stock_df.Close + (stock_df.Close / 40))
                    area_int = 0
                df_content.append(
                    textwrap.indent(
                        text=(textwrap.fill(article["summary"], 50)), prefix="<br>"
                    )
                )
                df_url.append(article["url"])
        else:
            pass

        # News Data
        df_news = pd.DataFrame(
            {
                "Title": df_title,
                "Current": df_current,
                "Content": df_content,
                "url": df_url,
            }
        )
        df_news = df_news.set_index(
            pd.to_datetime(df_date, utc=True).tz_convert(est_tz)
        )
        df_news = df_news.loc[
            (df_news.index >= df_stock.index[0]) & (df_news.index < df_stock.index[-1])
        ]
        customdatadf = np.stack((df_news["Content"], df_news["url"]), axis=-1)
        hover_temp = (
            "<br><b>News:%{text}</b><br><br>Summary:%{customdata[0]}<br>"
            "<b>Click On Marker For More</b><extra></extra>"
        )

        fig.add_trace(
            go.Scatter(
                name="News",
                x=df_news.index,
                y=df_news.Current,
                text=df_news.Title,
                customdata=customdatadf,
                hovertemplate=hover_temp,
                hoverinfo="text",
                mode="markers",
                marker_symbol="arrow-bar-down",
                marker=dict(
                    color="rgba(255, 215, 0, 0.9)",
                    size=10,
                    line=dict(color="gold", width=2),
                ),
            ),
            secondary_y=True,
            row=1,
            col=1,
        )
    if imps.PLT_WATERMARK:
        fig.add_layout_image(imps.PLT_WATERMARK)
    fig.add_annotation(
        xref="x domain",
        yref="y domain",
        text=f"Timezone: {dt_utcnow_local_tz().tzinfo}",
        x=0.02,
        y=1.015,
        font_size=10,
        showarrow=False,
    )
    if interval != 1440:
        fig.update_traces(xhoverformat="%I:%M%p %b %d '%y")
        fig.update_xaxes(
            tickformatstops=[
                dict(dtickrange=[None, 1_000], value="%I:%M%p \n%b, %d"),
                dict(dtickrange=[1_000, 60_000], value="%I:%M%p \n%b, %d"),
                dict(dtickrange=[60_000, 3_600_000], value="%I:%M%p \n%b, %d"),
                dict(dtickrange=[3_600_000, 86_400_000], value="%I:%M%p \n%b, %d"),
                dict(dtickrange=[86_400_000, 604_800_000], value="%b\n%d"),
                dict(dtickrange=[604_800_000, "M1"], value="%b\n%d"),
                dict(dtickrange=["M1", "M12"], value="%b '%y"),
                dict(dtickrange=["M12", None], value="%Y"),
            ],
        )
    fig.update_xaxes(showline=True)
    fig.update_yaxes(showline=True)
    fig.update_layout(
        margin=dict(l=0, r=10, t=40, b=20),
        template=imps.PLT_CANDLE_STYLE_TEMPLATE,
        yaxis2_title="Price",
        yaxis_title="Volume",
        font=imps.PLT_FONT,
        yaxis=dict(
            showgrid=False,
            fixedrange=False,
            side="left",
            titlefont=dict(color="#fdc708", size=12),
            tickfont=dict(
                color="#fdc708",
                size=12,
            ),
            nticks=20,
        ),
        yaxis2=dict(
            side="right",
            fixedrange=False,
            anchor="x",
            layer="above traces",
            overlaying="y",
            nticks=20,
            tickfont=dict(
                size=13,
            ),
            showline=False,
        ),
        xaxis=dict(
            rangeslider=dict(visible=False),
            type="date",
            tickfont=dict(
                size=10,
            ),
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        dragmode="pan",
        hovermode="x",
        spikedistance=1,
        hoverdistance=1,
        hoverlabel=dict(align="left"),
    )
    if futures in ticker.upper():
        fig.update_xaxes(
            rangebreaks=[
                dict(bounds=["sat", "sun"]),
                dict(bounds=[17, 17.50], pattern="hour"),
            ],
        )
    elif crypto not in ticker.upper() and interval != 1440:
        if extended_hours:
            unique = []
            for index in df_stock.index:
                dates = index.strftime("%Y-%m-%d")
                if dates in unique:  # pylint: disable=R1724
                    continue
                else:
                    unique.append(dates)
            fig.add_trace(
                go.Bar(
                    x=[0],
                    name="Pre-Market",
                    marker_color="LightSeaGreen",
                    opacity=0.2,
                ),
                secondary_y=False,
                row=1,
                col=1,
            )
            fig.add_trace(
                go.Bar(
                    x=[0],
                    name="After-Hours",
                    marker_color="blue",
                    opacity=0.3,
                ),
                secondary_y=False,
                row=1,
                col=1,
            )
            for dates in unique:
                fig.add_vrect(
                    x0=f"{dates} 04:00:00-05:00",
                    x1=f"{dates} 09:30:00-05:00",
                    fillcolor="LightSeaGreen",
                    opacity=0.1,
                    layer="below",
                    line_width=0,
                )
                fig.add_vrect(
                    x0=f"{dates} 16:00:00-05:00",
                    x1=f"{dates} 19:00:00-05:00",
                    fillcolor="blue",
                    opacity=0.1,
                    layer="below",
                    line_width=0,
                )
            fig.update_xaxes(
                rangebreaks=[
                    dict(bounds=["sat", "mon"]),
                    dict(bounds=[19.00, 4.00], pattern="hour"),
                ],
            )
        else:
            fig.update_xaxes(
                rangebreaks=[
                    dict(bounds=["sat", "mon"]),
                    dict(bounds=[16.00, 9.50], pattern="hour"),
                ],
            )
    if interval == 1440:
        fig.update_layout(
            xaxis_range=[
                (df_stock.index[0] - timedelta(days=10)),
                (dt_utcnow_local_tz() + timedelta(days=30)),
            ],
            xaxis_tickformatstops=[
                dict(dtickrange=[None, 604_800_000], value="%b\n%d"),
                dict(dtickrange=[604_800_000, "M1"], value="%b\n%d"),
                dict(dtickrange=["M1", "M12"], value="%b '%y"),
                dict(dtickrange=["M12", None], value="%Y"),
            ],
        )
        fig.update_xaxes(
            rangebreaks=[
                dict(bounds=["sat", "sun"]),
            ],
            tickformatstops=[
                dict(dtickrange=[None, 604_800_000], value="%b\n%d"),
                dict(dtickrange=[604_800_000, "M1"], value="%b\n%d"),
                dict(dtickrange=["M1", "M12"], value="%b '%y"),
                dict(dtickrange=["M12", None], value="%Y"),
            ],
        )
        fig.update_traces(xhoverformat="%b %d '%y")
    plt_title = (
        f"{ticker.upper()} {interval}min"
        if interval != 1440
        else f"{ticker.upper()} Daily"
    )

    return {"fig": fig, "bar_opacity": bar_opacity, "plt_title": plt_title}
