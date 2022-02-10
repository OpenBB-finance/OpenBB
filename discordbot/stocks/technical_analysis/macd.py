import os
import random
from datetime import datetime, timedelta

import disnake
import plotly.graph_objects as go
from PIL import Image
from plotly.subplots import make_subplots

import discordbot.config_discordbot as cfg
import discordbot.helpers
from discordbot.config_discordbot import logger
from discordbot.helpers import autocrop_image
from gamestonk_terminal.common.technical_analysis import momentum_model


async def macd_command(
    ctx, ticker="", fast="12", slow="26", signal="9", start="", end=""
):
    """Displays chart with moving average convergence/divergence [Yahoo Finance]"""

    try:

        # Debug
        if cfg.DEBUG:
            # pylint: disable=logging-too-many-args
            logger.debug(
                "!stocks.ta.macd %s %s %s %s %s %s",
                ticker,
                fast,
                slow,
                signal,
                start,
                end,
            )

        # Check for argument
        if ticker == "":
            raise Exception("Stock ticker is required")

        if start == "":
            start = datetime.now() - timedelta(days=365)
        else:
            start = datetime.strptime(start, cfg.DATE_FORMAT)

        if end == "":
            end = datetime.now()
        else:
            end = datetime.strptime(end, cfg.DATE_FORMAT)

        if not fast.lstrip("-").isnumeric():
            raise Exception("Number has to be an integer")
        fast = float(fast)
        if not slow.lstrip("-").isnumeric():
            raise Exception("Number has to be an integer")
        slow = float(slow)
        if not signal.lstrip("-").isnumeric():
            raise Exception("Number has to be an integer")
        signal = float(signal)

        ticker = ticker.upper()
        df_stock = discordbot.helpers.load(ticker, start)
        if df_stock.empty:
            raise Exception("Stock ticker is invalid")

        # Retrieve Data
        df_stock = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]

        df_ta = momentum_model.macd(df_stock["Adj Close"], fast, slow, signal)
        trace_name = df_ta.columns[0].replace("_", " ")

        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.07,
            row_width=[0.5, 0.6],
        )
        fig.add_trace(
            go.Scatter(
                name=ticker,
                x=df_stock.index,
                y=df_stock["Adj Close"].values,
                line=dict(color="#fdc708", width=2),
                opacity=1,
                showlegend=False,
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Bar(
                name="MACD Histogram",
                x=df_ta.index,
                y=df_ta.iloc[:, 1].values,
                opacity=1,
            ),
            row=2,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                mode="lines",
                name="MACD Line",
                x=df_ta.index,
                y=df_ta.iloc[:, 0].values,
                opacity=1,
            ),
            row=2,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                mode="lines",
                name="Signal Line",
                x=df_ta.index,
                y=df_ta.iloc[:, 2].values,
                opacity=1,
            ),
            row=2,
            col=1,
        )
        fig.update_layout(
            margin=dict(l=0, r=20, t=30, b=20),
            template=cfg.PLT_TA_STYLE_TEMPLATE,
            colorway=cfg.PLT_TA_COLORWAY,
            title=f"{ticker} {trace_name}",
            title_x=0.3,
            yaxis_title="Stock Price ($)",
            yaxis=dict(
                fixedrange=False,
            ),
            xaxis=dict(
                rangeslider=dict(visible=False),
                type="date",
            ),
            dragmode="pan",
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
        )
        config = dict({"scrollZoom": True})
        imagefile = "ta_macd.png"

        # Check if interactive settings are enabled
        plt_link = ""
        if cfg.INTERACTIVE:
            html_ran = random.randint(69, 69420)
            fig.write_html(f"in/macd_{html_ran}.html", config=config)
            plt_link = f"[Interactive]({cfg.INTERACTIVE_URL}/macd_{html_ran}.html)"

        fig.update_layout(
            width=800,
            height=500,
        )
        fig.write_image(imagefile)

        img = Image.open(imagefile)
        print(img.size)
        im_bg = Image.open(cfg.IMG_BG)
        h = img.height + 240
        w = img.width + 520

        # Paste fig onto background img and autocrop background
        img = img.resize((w, h), Image.ANTIALIAS)
        x1 = int(0.5 * im_bg.size[0]) - int(0.5 * img.size[0])
        y1 = int(0.5 * im_bg.size[1]) - int(0.5 * img.size[1])
        x2 = int(0.5 * im_bg.size[0]) + int(0.5 * img.size[0])
        y2 = int(0.5 * im_bg.size[1]) + int(0.5 * img.size[1])
        img = img.convert("RGB")
        im_bg.paste(img, box=(x1 - 5, y1, x2 - 5, y2))
        im_bg.save(imagefile, "PNG", quality=100)
        image = Image.open(imagefile)
        image = autocrop_image(image, 0)
        image.save(imagefile, "PNG", quality=100)

        image = disnake.File(imagefile)

        print(f"Image {imagefile}")
        if cfg.DEBUG:
            logger.debug("Image: %s", imagefile)
        title = "Stocks: Moving-Average-Convergence-Divergence " + ticker
        embed = disnake.Embed(title=title, description=plt_link, colour=cfg.COLOR)
        embed.set_image(url=f"attachment://{imagefile}")
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        os.remove(imagefile)

        await ctx.send(embed=embed, file=image)

    except Exception as e:
        embed = disnake.Embed(
            title="ERROR Stocks: Moving-Average-Convergence-Divergence",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
