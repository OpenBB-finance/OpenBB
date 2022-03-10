import plotly.graph_objects as go
import yfinance as yf
from plotly.subplots import make_subplots

import bots.config_discordbot as cfg
from bots import helpers


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
            increasing_line_color="#00ACFF",
            decreasing_line_color="#e4003a",
        ),
        row=1,
        col=1,
    )
    colors = [
        "#00ACFF" if row.Open < row["Close"] else "#e4003a"
        for _, row in df_hist.iterrows()
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
    if cfg.PLT_WATERMARK:
        fig.add_layout_image(cfg.PLT_WATERMARK)
    fig.update_layout(
        margin=dict(l=0, r=0, t=25, b=5),
        template=cfg.PLT_CANDLE_STYLE_TEMPLATE,
        showlegend=False,
        yaxis_title="Premium",
        font=cfg.PLT_FONT,
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

    imagefile = "opt_hist.png"

    # Check if interactive settings are enabled
    plt_link = ""
    if cfg.INTERACTIVE:
        plt_link = helpers.inter_chart(fig, imagefile, callback=False)

    fig.update_layout(
        width=800,
        height=500,
    )

    imagefile = helpers.image_border(imagefile, fig=fig)

    return {
        "title": f"{ticker.upper()} {strike} {opt_type} expiring {expiry} Historical",
        "description": plt_link,
        "imagefile": imagefile,
    }
