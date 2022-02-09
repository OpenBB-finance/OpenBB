import os
import random

import bots.config_discordbot as cfg
import disnake
import plotly.graph_objects as go
import yfinance as yf
from bots.config_discordbot import logger
from bots.helpers import autocrop_image
from gamestonk_terminal.stocks.dark_pool_shorts import finra_model
from PIL import Image
from plotly.subplots import make_subplots


async def dpotc_command(ctx, ticker: str = ""):
    """Dark pools (ATS) vs OTC data [FINRA]"""

    try:
        # Debug user input
        if cfg.DEBUG:
            logger.debug("!stocks.dps.dpotc %s", ticker)

        # Check for argument
        if ticker == "":
            raise Exception("Stock ticker is required")

        ticker = ticker.upper()

        stock = yf.download(ticker, progress=False)
        if stock.empty:
            raise Exception("Stock ticker is invalid")

        # Retrieve data
        ats, otc = finra_model.getTickerFINRAdata(ticker)

        # Debug user output
        if cfg.DEBUG:
            logger.debug(ats.to_string())
            logger.debug(otc.to_string())

        # Output data
        title = f"Stocks: [FINRA] Dark Pools (ATS) vs OTC {ticker}"

        if ats.empty and otc.empty:
            raise Exception("Stock ticker is invalid")

        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.07,
            row_width=[0.4, 0.6],
            specs=[[{"secondary_y": True}], [{"secondary_y": False}]],
        )

        if not ats.empty and not otc.empty:
            fig.add_trace(
                go.Bar(
                    x=ats.index,
                    y=(
                        ats["totalWeeklyShareQuantity"]
                        + otc["totalWeeklyShareQuantity"]
                    ),
                    name="ATS",
                    opacity=0.8,
                ),
                row=1,
                col=1,
                secondary_y=False,
            )
            fig.add_trace(
                go.Bar(
                    x=otc.index,
                    y=otc["totalWeeklyShareQuantity"],
                    name="OTC",
                    opacity=0.8,
                    yaxis="y2",
                    offset=0.0001,
                ),
                row=1,
                col=1,
            )

        elif not ats.empty:
            fig.add_trace(
                go.Bar(
                    x=ats.index,
                    y=(
                        ats["totalWeeklyShareQuantity"]
                        + otc["totalWeeklyShareQuantity"]
                    ),
                    name="ATS",
                    opacity=0.8,
                ),
                row=1,
                col=1,
                secondary_y=False,
            )

        elif not otc.empty:
            fig.add_trace(
                go.Bar(
                    x=otc.index,
                    y=otc["totalWeeklyShareQuantity"],
                    name="OTC",
                    opacity=0.8,
                    yaxis="y2",
                    secondary_y=False,
                ),
                row=1,
                col=1,
            )

        if not ats.empty:
            fig.add_trace(
                go.Scatter(
                    name="ATS",
                    x=ats.index,
                    y=ats["totalWeeklyShareQuantity"] / ats["totalWeeklyTradeCount"],
                    line=dict(color="#fdc708", width=2),
                    opacity=1,
                    showlegend=False,
                    yaxis="y2",
                ),
                row=2,
                col=1,
            )

            if not otc.empty:
                fig.add_trace(
                    go.Scatter(
                        name="OTC",
                        x=otc.index,
                        y=otc["totalWeeklyShareQuantity"]
                        / otc["totalWeeklyTradeCount"],
                        line=dict(color="#d81aea", width=2),
                        opacity=1,
                        showlegend=False,
                    ),
                    row=2,
                    col=1,
                )
        else:
            fig.add_trace(
                go.Scatter(
                    name="OTC",
                    x=otc.index,
                    y=otc["totalWeeklyShareQuantity"] / otc["totalWeeklyTradeCount"],
                    line=dict(color="#d81aea", width=2),
                    opacity=1,
                    showlegend=False,
                ),
                row=2,
                col=1,
            )

        fig.update_xaxes(showspikes=True, spikesnap="cursor", spikemode="across")
        fig.update_yaxes(showspikes=True, spikethickness=2)
        fig.update_layout(
            margin=dict(l=20, r=0, t=10, b=20),
            template=cfg.PLT_CANDLE_STYLE_TEMPLATE,
            colorway=cfg.PLT_TA_COLORWAY,
            title=f"Dark Pools (ATS) vs OTC (Non-ATS) Data for {ticker}",
            title_x=0.5,
            yaxis3_title="Shares per Trade",
            yaxis_title="Total Weekly Shares",
            xaxis2_title="Weeks",
            yaxis=dict(
                fixedrange=False,
                side="left",
                nticks=20,
            ),
            yaxis2=dict(
                fixedrange=False,
                showgrid=False,
                overlaying="y",
                anchor="x",
                layer="above traces",
            ),
            yaxis3=dict(
                fixedrange=False,
                nticks=10,
            ),
            xaxis=dict(
                rangeslider=dict(visible=False),
                type="date",
                showspikes=True,
                nticks=20,
            ),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
            barmode="group",
            bargap=0.5,
            bargroupgap=0,
            dragmode="pan",
            hovermode="x unified",
            spikedistance=1000,
            hoverdistance=100,
        )
        config = dict({"scrollZoom": True})
        rand = random.randint(69, 69420)
        imagefile = f"dps_dpotc{rand}.png"

        # Check if interactive settings are enabled
        plt_link = ""
        if cfg.INTERACTIVE:
            fig.write_html(f"in/dpotc_{rand}.html", config=config)
            plt_link = f"[Interactive]({cfg.INTERACTIVE_URL}/dpotc_{rand}.html)"

        fig.update_layout(
            width=800,
            height=500,
        )
        fig.write_image(imagefile)

        img = Image.open(imagefile)
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
        if cfg.DEBUG:
            print(f"Image: {imagefile}")
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
            title=f"ERROR Stocks: [FINRA] Dark Pools (ATS) vs OTC {ticker}",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
