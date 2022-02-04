import os
import random
import time

import disnake
import plotly.graph_objects as go
from PIL import Image
from plotly.subplots import make_subplots

import discordbot.config_discordbot as cfg
from discordbot.helpers import autocrop_image
from gamestonk_terminal.stocks.options import syncretism_model

startTime = time.time()


async def hist_command(
    ctx,
    ticker: str = None,
    expiry: str = "",
    strike: float = 10,
    opt_type: str = "",
    greek: str = "",
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
    try:

        # Debug
        if cfg.DEBUG:
            print(f"opt-hist {ticker} {strike} {opt_type} {expiry} {greek}")

        # Check for argument
        if ticker is None:
            raise Exception("Stock ticker is required")

        if opt_type == "Puts":
            put = bool(True)
        if opt_type == "Calls":
            put = bool(False)
        chain_id = ""

        df_hist = syncretism_model.get_historical_greeks(
            ticker, expiry, chain_id, strike, put
        )
        title = f"\n{ticker.upper()} {strike} {opt_type} expiring {expiry} Historical {greek.upper()}"
        # Output data
        fig = make_subplots(shared_xaxes=True, specs=[[{"secondary_y": True}]])

        fig.add_trace(
            go.Scatter(
                name=ticker.upper(),
                x=df_hist.index,
                y=df_hist.price,
                line=dict(color="#fdc708", width=2),
                opacity=1,
            ),
        )
        fig.add_trace(
            go.Scatter(
                name="Premium",
                x=df_hist.index,
                y=df_hist["premium"],
                opacity=1,
                yaxis="y2",
            ),
        )
        if greek:
            fig.add_trace(
                go.Scatter(
                    name=f"{greek.upper()}",
                    x=df_hist.index,
                    y=df_hist[greek],
                    opacity=1,
                    yaxis="y3",
                ),
            )
        fig.update_layout(
            margin=dict(l=10, r=10, t=30, b=20),
            template=cfg.PLT_TA_STYLE_TEMPLATE,
            colorway=cfg.PLT_TA_COLORWAY,
            title=title,
            title_x=0.03,
            yaxis_title="<b>Stock Price</b> ($)",
            yaxis=dict(
                side="right",
                fixedrange=False,
                titlefont=dict(color="#fdc708"),
                tickfont=dict(color="#fdc708"),
                position=0.02,
                nticks=20,
            ),
            xaxis=dict(
                rangeslider=dict(visible=False),
                type="date",
                fixedrange=False,
                domain=[0.037, 1],
            ),
            xaxis2=dict(
                rangeslider=dict(visible=False),
                type="date",
                fixedrange=False,
            ),
            xaxis3=dict(
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
                fixedrange=False,
                anchor="x",
                overlaying="y",
                titlefont=dict(color="#d81aea"),
                tickfont=dict(color="#d81aea"),
                nticks=20,
            ),
            yaxis3=dict(
                side="left",
                position=0,
                fixedrange=False,
                overlaying="y",
                titlefont=dict(color="#00e6c3"),
                tickfont=dict(color="#00e6c3"),
                nticks=20,
            ),
            hovermode="x unified",
        )
        config = dict({"scrollZoom": True})
        rand = random.randint(69, 69420)
        imagefile = f"opt_hist{rand}.png"

        # Check if interactive settings are enabled
        plt_link = ""
        if cfg.INTERACTIVE:
            fig.write_html(f"in/hist_{rand}.html", config=config)
            plt_link = f"[Interactive]({cfg.INTERACTIVE_URL}/hist_{rand}.html)"

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
        title = f"{ticker.upper()} {strike} {opt_type} expiring {expiry} Historical"
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
            title="ERROR Options: History",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)


executionTime = time.time() - startTime
print(f"> Extension {__name__} is ready: time in seconds: {str(executionTime)}\n")
