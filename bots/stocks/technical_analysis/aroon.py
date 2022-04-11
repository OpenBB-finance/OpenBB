import logging

import plotly.graph_objects as go

from bots import imps, load_candle
from openbb_terminal.common.technical_analysis import trend_indicators_model
from openbb_terminal.decorators import log_start_end

# pylint: disable=R0913

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def aroon_command(
    ticker="",
    interval: int = 15,
    past_days: int = 0,
    length="25",
    scalar="100",
    start="",
    end="",
    extended_hours: bool = False,
    heikin_candles: bool = False,
    trendline: bool = False,
    news: bool = False,
):
    """Displays chart with aroon indicator [Yahoo Finance]"""

    # Debug
    if imps.DEBUG:
        logger.debug(
            "ta aroon %s %s %s %s %s %s %s %s %s %s %s",
            ticker,
            interval,
            past_days,
            length,
            scalar,
            start,
            end,
            extended_hours,
            heikin_candles,
            trendline,
            news,
        )

    # Check for argument
    if ticker == "":
        raise Exception("Stock ticker is required")

    if not length.lstrip("-").isnumeric():
        raise Exception("Number has to be an integer")
    length = int(length)
    if not scalar.lstrip("-").isnumeric():
        raise Exception("Number has to be an integer")
    scalar = float(scalar)

    # Retrieve Data
    df_stock, start, end, bar_start = load_candle.stock_data(
        ticker=ticker,
        interval=interval,
        past_days=past_days,
        extended_hours=extended_hours,
        start=start,
        end=end,
        heikin_candles=heikin_candles,
    )

    if df_stock.empty:
        raise Exception("No Data Found")

    df_ta = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]
    df_ta = df_ta.join(
        trend_indicators_model.aroon(df_ta["High"], df_ta["Low"], length, scalar)
    )

    # Output Data
    if interval != 1440:
        df_ta = df_ta.loc[(df_ta.index >= bar_start) & (df_ta.index < end)]
    df_ta = df_ta.fillna(0.0)

    plot = load_candle.candle_fig(
        df_ta,
        ticker,
        interval,
        extended_hours,
        news,
        bar=bar_start,
        int_bar=interval,
        trendline=trendline,
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_width=[0.15, 0.15, 0.7],
        specs=[
            [{"secondary_y": True}],
            [{"secondary_y": False}],
            [{"secondary_y": False}],
        ],
    )
    title = f"<b>{plot['plt_title']} Aroon ({length})</b>"
    fig = plot["fig"]
    idx = 6 if (not trendline) and (interval != 1440) else 11

    fig.add_trace(
        go.Scatter(
            name="Aroon DOWN",
            mode="lines",
            x=df_ta.index,
            y=df_ta.iloc[:, idx].values,
            opacity=1,
            yaxis="y3",
            showlegend=False,
        ),
        row=2,
        col=1,
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            name="Aroon UP",
            mode="lines",
            x=df_ta.index,
            y=df_ta.iloc[:, (idx + 1)].values,
            opacity=1,
            yaxis="y3",
            showlegend=False,
        ),
        row=2,
        col=1,
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            name="Aroon OSC",
            mode="lines",
            x=df_ta.index,
            y=df_ta.iloc[:, (idx + 2)].values,
            opacity=1,
            yaxis="y4",
            showlegend=False,
        ),
        row=3,
        col=1,
        secondary_y=False,
    )
    fig.add_hline(
        y=50,
        fillcolor="grey",
        opacity=1,
        layer="below",
        line_width=3,
        line=dict(color="grey", dash="dash"),
        row=2,
        col=1,
    )
    fig.add_annotation(
        xref="paper",
        yref="paper",
        text="Aroon DOWN",
        x=-0.07,
        y=0.18,
        font_size=10,
        font_color="#00e6c3",
        showarrow=False,
    )
    fig.add_annotation(
        xref="paper",
        yref="paper",
        text="Aroon UP",
        x=-0.07,
        y=0.25,
        font_size=10,
        font_color="#9467bd",
        showarrow=False,
    )
    fig.add_annotation(
        xref="paper",
        yref="paper",
        text="Aroon OSC",
        x=-0.07,
        y=0.1,
        font_size=10,
        font_color="#e250c3",
        showarrow=False,
    )
    fig.update_layout(
        margin=dict(l=10, r=0, t=50, b=20),
        template=imps.PLT_TA_STYLE_TEMPLATE,
        colorway=imps.PLT_TA_COLORWAY,
        title=title,
        title_x=0.1,
        title_font_size=14,
        dragmode="pan",
        yaxis=dict(nticks=10),
        yaxis2=dict(nticks=10),
        yaxis3=dict(
            side="right",
            fixedrange=False,
            nticks=5,
            titlefont=dict(size=10),
            tickfont=dict(
                size=9,
            ),
            showline=False,
        ),
        yaxis4=dict(
            side="right",
            fixedrange=False,
            nticks=10,
            titlefont=dict(size=10),
            tickfont=dict(
                size=9,
            ),
            showline=False,
        ),
    )
    imagefile = "ta_aroon.png"

    # Check if interactive settings are enabled
    plt_link = ""
    if imps.INTERACTIVE:
        plt_link = imps.inter_chart(fig, imagefile, callback=False)
    imagefile = imps.image_border(imagefile, fig=fig)

    return {
        "title": f"Stocks: Aroon-Indicator {ticker.upper()}",
        "description": plt_link,
        "imagefile": imagefile,
    }
