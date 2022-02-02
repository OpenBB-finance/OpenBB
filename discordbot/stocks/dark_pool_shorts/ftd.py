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
from gamestonk_terminal.stocks.dark_pool_shorts import sec_model


async def ftd_command(ctx, ticker: str = "", start="", end=""):
    """Fails-to-deliver data [SEC]"""
    try:
        # Debug user input
        if cfg.DEBUG:
            logger.debug("!stocks.dps.ftd %s %s %s", ticker, start, end)

        # Check for argument
        if ticker == "":
            raise Exception("Stock ticker is required")

        ticker = ticker.upper()

        if start == "":
            start = datetime.now() - timedelta(days=365)
        else:
            start = datetime.strptime(start, cfg.DATE_FORMAT)

        if end == "":
            end = datetime.now()
        else:
            end = datetime.strptime(end, cfg.DATE_FORMAT)

        # Retrieve data
        ftds_data = sec_model.get_fails_to_deliver(ticker, start, end, 0)

        # Debug user output
        if cfg.DEBUG:
            logger.debug(ftds_data.to_string())

        stock = discordbot.helpers.load(ticker, start)
        stock_ftd = stock[stock.index > start]
        stock_ftd = stock_ftd[stock_ftd.index < end]

        # Output data
        fig = make_subplots(shared_xaxes=True, specs=[[{"secondary_y": True}]])

        fig.add_trace(
            go.Scatter(
                name=ticker,
                x=stock_ftd.index,
                y=stock_ftd["Adj Close"],
                line=dict(color="#fdc708", width=2),
                opacity=1,
                showlegend=False,
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Bar(
                name="FTDs",
                x=ftds_data["SETTLEMENT DATE"],
                y=ftds_data["QUANTITY (FAILS)"] / 1000,
                opacity=1,
            ),
            secondary_y=True,
        )
        # Set y-axes titles
        fig.update_yaxes(title_text="<b>Shares</b> [K]", secondary_y=True)
        fig.update_layout(
            margin=dict(l=0, r=20, t=30, b=20),
            template=cfg.PLT_TA_STYLE_TEMPLATE,
            colorway=cfg.PLT_TA_COLORWAY,
            title=f"{ticker}",
            title_x=0.5,
            yaxis_title="<b>Stock Price</b> ($)",
            yaxis=dict(
                side="right",
                fixedrange=False,
            ),
            xaxis=dict(
                rangeslider=dict(visible=False),
                type="date",
                fixedrange=False,
            ),
            xaxis2=dict(
                rangeslider=dict(visible=False),
                type="date",
                fixedrange=False,
            ),
            dragmode="pan",
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
            yaxis2=dict(
                side="left",
                position=0.15,
                fixedrange=False,
            ),
            hovermode="x unified",
        )
        config = dict({"scrollZoom": True})
        imagefile = "dps_ftd.png"

        # Check if interactive settings are enabled
        plt_link = ""
        if cfg.INTERACTIVE:
            html_ran = random.randint(69, 69420)
            fig.write_html(f"in/ftds_{html_ran}.html", config=config)
            plt_link = f"[Interactive]({cfg.INTERACTIVE_URL}/ftds_{html_ran}.html)"

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
        title = "Stocks: [SEC] Failure-to-deliver " + ticker
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
            title="ERROR Stocks: [SEC] Failure-to-deliver",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
