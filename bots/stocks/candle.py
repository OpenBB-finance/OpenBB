from datetime import datetime, timedelta

import bots.config_discordbot as cfg
import plotly.graph_objects as go
import yfinance as yf
from bots import helpers
from bots.config_discordbot import logger
from gamestonk_terminal.common.technical_analysis import overlap_model
from plotly.subplots import make_subplots


def candle_command(
    ticker: str = "",
    interval: int = 15,
    past_days: int = 1,
    start="",
    end="",
):
    """Shows candle plot of loaded ticker. [Source: Yahoo Finance, IEX Cloud or Alpha Vantage]

    Parameters
    ----------
    ticker: str
        Ticker name
    interval: int
        chart mins or daily
    past_days: int
        Display the past * days. Default: 1(Not for Daily)
    start: str
        start date format YYYY-MM-DD
    end: str
        end date format YYYY-MM-DD
    """

    logger.info("candle %s %s %s %s", ticker, interval, start, end)

    if start == "":
        start = datetime.now() - timedelta(days=365)
    else:
        start = datetime.strptime(start, cfg.DATE_FORMAT)
    if end == "":
        end = datetime.now()
    else:
        end = datetime.strptime(end, cfg.DATE_FORMAT)

    futures = "=F" or "^"
    crypto = "-USD"
    if interval == 1440:
        df_stock_candidate = yf.download(
            ticker,
            start=start,
            end=end,
            progress=False,
        )

        df_stock_candidate.index.name = "date"
    else:
        s_int = str(interval) + "m"
        d_granularity = {
            "1m": past_days,
            "5m": past_days,
            "15m": past_days,
            "30m": past_days,
            "60m": past_days,
        }
        s_start_dt = datetime.utcnow() - timedelta(days=d_granularity[s_int])
        s_date_start = s_start_dt.strftime("%Y-%m-%d")

        df_stock_candidate = yf.download(
            ticker,
            start=s_date_start if s_start_dt > start else start.strftime("%Y-%m-%d"),
            progress=False,
            interval=s_int,
            prepost=True,
        )

    # Check that loading a stock was not successful
    if df_stock_candidate.empty:
        raise Exception(f"No data found for {ticker.upper()}.")

    df_stock_candidate.index = df_stock_candidate.index.tz_localize(None)
    df_stock_candidate.index.name = "date"
    df_stock = df_stock_candidate
    price_df = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]

    df_vwap = overlap_model.vwap(price_df, 0)

    plt_title = [f"{ticker.upper()} Intraday {interval}min", "Volume"]
    title = f"Intraday {interval}min Chart for {ticker.upper()}"
    if interval == 1440:
        plt_title = [f"{ticker.upper()} Daily", "Volume"]
        title = f"Daily Chart for {ticker.upper()}"

    fig = make_subplots(
        shared_xaxes=True,
        vertical_spacing=0.09,
        subplot_titles=plt_title,
        specs=[[{"secondary_y": True}]],
    )
    fig.add_trace(
        go.Candlestick(
            x=df_stock.index,
            open=df_stock.Open,
            high=df_stock.High,
            low=df_stock.Low,
            close=df_stock.Close,
            name="OHLC",
            showlegend=False,
        ),
        secondary_y=True,
    )
    fig.add_trace(
        go.Bar(
            x=df_stock.index,
            y=df_stock.Volume,
            name="Volume",
            yaxis="y2",
            marker_color="#d81aea",
            opacity=0.4,
            showlegend=False,
        ),
        secondary_y=False,
    )
    if interval != 1440:
        fig.add_trace(
            go.Scatter(
                name="VWAP",
                x=df_stock.index,
                y=df_vwap["VWAP_D"],
                opacity=0.65,
                line=dict(color="#fdc708", width=2),
                showlegend=True,
            ),
            secondary_y=True,
        )
    fig.update_xaxes(showspikes=True, spikesnap="cursor", spikemode="across")
    fig.update_yaxes(showspikes=True, spikethickness=2)
    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=20),
        template=cfg.PLT_CANDLE_STYLE_TEMPLATE,
        yaxis2_title="Price ($)",
        yaxis_title="Volume",
        yaxis=dict(
            showgrid=False,
            fixedrange=False,
            side="left",
            titlefont=dict(color="#d81aea"),
            tickfont=dict(color="#d81aea"),
            nticks=20,
        ),
        yaxis2=dict(
            side="right",
            fixedrange=False,
            anchor="x",
            layer="above traces",
            overlaying="y",
            nticks=20,
        ),
        xaxis=dict(
            rangeslider=dict(visible=False),
            type="date",
            showspikes=True,
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        dragmode="pan",
        hovermode="x unified",
        spikedistance=1000,
        hoverdistance=100,
    )
    if futures in ticker.upper():
        fig.update_xaxes(
            rangebreaks=[
                dict(bounds=["sat", "sun"]),
                dict(bounds=[17, 17.50], pattern="hour"),
            ],
        )
    elif crypto not in ticker.upper() and interval != 1440:
        fig.update_xaxes(
            rangebreaks=[
                dict(bounds=["sat", "mon"]),
                dict(bounds=[20, 9.50], pattern="hour"),
            ],
        )
    config = dict({"scrollZoom": True})
    imagefile = "candle.png"

    # Check if interactive settings are enabled
    plt_link = ""
    if cfg.INTERACTIVE:
        html_ran = helpers.uuid_get()
        fig.write_html(f"in/candle_{html_ran}.html", config=config)
        plt_link = f"[Interactive]({cfg.INTERACTIVE_URL}/candle_{html_ran}.html)"

    fig.update_layout(
        width=800,
        height=500,
    )
    imagefile = helpers.image_border(imagefile, fig=fig)

    return {
        "title": title,
        "description": plt_link,
        "imagefile": imagefile,
    }
