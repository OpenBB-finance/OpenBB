import os
import random
from datetime import datetime, timedelta

import disnake
import pandas as pd
import plotly.graph_objects as go
from PIL import Image

import discordbot.config_discordbot as cfg
import discordbot.helpers
from discordbot.config_discordbot import logger
from discordbot.helpers import autocrop_image
from gamestonk_terminal.common.technical_analysis import overlap_model


async def hma_command(ctx, ticker="", window="", offset="", start="", end=""):
    """Displays chart with hull moving average [Yahoo Finance]"""

    try:
        # Debug
        if cfg.DEBUG:
            logger.debug(
                "!stocks.ta.hma %s %s %s %s %s",
                ticker,
                window,
                offset,
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

        l_legend = [ticker]

        if window == "":
            window = [20, 50]
        else:
            window_temp = list()
            for wind in window.split(","):
                try:
                    window_temp.append(float(wind))
                except Exception as e:
                    raise Exception("Window needs to be a float") from e
            window = window_temp

        ticker = ticker.upper()
        stock = discordbot.helpers.load(ticker, start)
        if stock.empty:
            raise Exception("Stock ticker is invalid")

        # Retrieve Data
        price_df = pd.DataFrame(
            stock["Adj Close"].values, columns=["Price"], index=stock.index
        )
        i = 1
        for win in window:
            hma_data = overlap_model.hma(
                values=stock["Adj Close"], length=win, offset=offset
            )
            price_df = price_df.join(hma_data)
            l_legend.append(f"HMA {win}")
            i += 1

        # Output Data
        start = start.strftime("%Y-%m-%d")
        end = end.strftime("%Y-%m-%d")
        price_df = price_df.loc[(price_df.index >= start) & (price_df.index < end)]

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                name=f"{ticker}",
                x=price_df.index,
                y=price_df["Price"],
                line=dict(color="#fdc708", width=2),
                opacity=1,
            ),
        )
        for i in range(1, price_df.shape[1]):
            trace_name = price_df.columns[i].replace("_", " ")
            fig.add_trace(
                go.Scatter(
                    name=trace_name,
                    x=price_df.index,
                    y=price_df.iloc[:, i],
                    opacity=1,
                ),
            )
        fig.update_layout(
            margin=dict(l=0, r=0, t=50, b=20),
            template=cfg.PLT_TA_STYLE_TEMPLATE,
            colorway=cfg.PLT_TA_COLORWAY,
            title=f"{ticker} HMA",
            title_x=0.5,
            yaxis_title="Stock Price ($)",
            xaxis_title="Time",
            yaxis=dict(
                fixedrange=False,
            ),
            xaxis=dict(
                rangeslider=dict(visible=False),
                type="date",
            ),
            dragmode="pan",
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        )
        config = dict({"scrollZoom": True})
        imagefile = "ta_hma.png"

        # Check if interactive settings are enabled
        plt_link = ""
        if cfg.INTERACTIVE:
            html_ran = random.randint(69, 69420)
            fig.write_html(f"in/hma_{html_ran}.html", config=config)
            plt_link = f"[Interactive]({cfg.INTERACTIVE_URL}/hma_{html_ran}.html)"

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
        title = "Stocks: Hull-Moving-Average  " + ticker
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
            title="ERROR Stocks: Hull-Moving-Average",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
