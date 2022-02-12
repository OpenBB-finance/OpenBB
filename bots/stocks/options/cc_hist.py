import numpy as np
import plotly.graph_objects as go
import yfinance as yf
from plotly.subplots import make_subplots

import bots.config_discordbot as cfg
from bots.helpers import image_border


def cc_hist_command(
    ticker: str = None, expiry: str = "", strike: float = 10, opt_type: str = ""
):
    """Plot historical option prices

    Parameters
    ----------
    ticker: str
        Stock ticker
    expiry: str
        expiration date
    strike: float
        Option strike price
    put: bool
        Calls for call
        Puts for put
    """

    # Debug
    if cfg.DEBUG:
        print(f"opt-hist {ticker} {strike} {opt_type} {expiry}")

    # Check for argument
    if ticker is None:
        raise Exception("Stock ticker is required")
    yf_ticker = yf.Ticker(ticker)
    dates = list(yf_ticker.options)

    if not dates:
        raise Exception("Stock ticker is invalid")

    options = yf.Ticker(ticker).option_chain(expiry)

    if opt_type == "Calls":
        options = options.calls
    if opt_type == "Puts":
        options = options.puts

    chain_id = options.loc[options.strike == strike, "contractSymbol"].values[0]
    df_hist = yf.download(chain_id)
    df_hist.index.name = "date"

    plt_title = [
        f"\n{ticker.upper()} {strike} {opt_type} expiring {expiry} Historical",
        "Volume",
    ]

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        subplot_titles=plt_title,
        row_width=[0.2, 0.7],
    )
    fig.add_trace(
        go.Candlestick(
            x=df_hist.index,
            open=df_hist.Open,
            high=df_hist.High,
            low=df_hist.Low,
            close=df_hist.Close,
            name="OHLC",
        ),
        row=1,
        col=1,
    )
    colors = [
        "green" if row.Open < row["Close"] else "red" for _, row in df_hist.iterrows()
    ]  # pylint: disable=E1120
    fig.add_trace(
        go.Bar(
            x=df_hist.index,
            y=df_hist.Volume,
            name="Volume",
            marker_color=colors,
        ),
        row=2,
        col=1,
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=25, b=5),
        template=cfg.PLT_CANDLE_STYLE_TEMPLATE,
        showlegend=False,
        yaxis_title="Premium",
        xaxis=dict(
            rangeslider=dict(visible=False),
            type="date",
        ),
        dragmode="pan",
    )
    fig.update_xaxes(
        rangebreaks=[
            dict(bounds=["sat", "mon"]),
        ],
    )
    config = dict({"scrollZoom": True})
    rand = np.random.randint(70000)
    imagefile = f"opt_hist{rand}.png"
    fig.write_image(imagefile)
    imagefile = image_border(imagefile)

    # Check if interactive settings are enabled
    plt_link = ""
    if cfg.INTERACTIVE:
        fig.write_html(f"in/cc_hist_{rand}.html", config=config)
        plt_link = f"[Interactive]({cfg.INTERACTIVE_URL}/cc_hist_{rand}.html)"

    return {
        "title": f"{ticker.upper()} {strike} {opt_type} expiring {expiry} Historical",
        "description": plt_link,
        "imagefile": imagefile,
    }
