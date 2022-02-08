import os
import random
import time

import disnake
import pandas as pd
import plotly.graph_objects as go
from PIL import Image

import discordbot.config_discordbot as cfg
from discordbot.helpers import autocrop_image
from gamestonk_terminal.stocks.options import op_helpers, yfinance_model

startTime = time.time()


async def oi_command(
    ctx,
    ticker: str = None,
    expiry: str = "",
    min_sp: float = None,
    max_sp: float = None,
):
    """Options OI"""

    try:

        # Debug
        print(f"!stocks.opt.oi {ticker} {expiry} {min_sp} {max_sp}")

        # Check for argument
        if ticker is None:
            raise Exception("Stock ticker is required")

        dates = yfinance_model.option_expirations(ticker)

        if not dates:
            raise Exception("Stock ticker is invalid")

        options = yfinance_model.get_option_chain(ticker, expiry)
        calls = options.calls
        puts = options.puts
        current_price = yfinance_model.get_price(ticker)

        min_strike = 0.75 * current_price
        max_strike = 1.95 * current_price

        if len(calls) > 40:
            min_strike = 0.75 * current_price
            max_strike = 1.25 * current_price

        if min_sp:
            min_strike = min_sp
        if max_sp:
            max_strike = max_sp

        call_oi = calls.set_index("strike")["openInterest"] / 1000
        put_oi = puts.set_index("strike")["openInterest"] / 1000

        df_opt = pd.merge(call_oi, put_oi, left_index=True, right_index=True)
        df_opt = df_opt.rename(
            columns={"openInterest_x": "OI_call", "openInterest_y": "OI_put"}
        )

        max_pain = op_helpers.calculate_max_pain(df_opt)
        fig = go.Figure()

        dmax = df_opt[["OI_call", "OI_put"]].values.max()
        dmin = df_opt[["OI_call", "OI_put"]].values.min()
        fig.add_trace(
            go.Scatter(
                x=df_opt.index,
                y=df_opt["OI_call"],
                name="Calls",
                mode="lines+markers",
                line=dict(color="green", width=3),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=df_opt.index,
                y=df_opt["OI_put"],
                name="Puts",
                mode="lines+markers",
                line=dict(color="red", width=3),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[current_price, current_price],
                y=[dmin, dmax],
                mode="lines",
                line=dict(color="gold", width=2),
                name="Current Price",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[max_pain, max_pain],
                y=[dmin, dmax],
                mode="lines",
                line=dict(color="grey", width=3, dash="dash"),
                name=f"Max Pain: {max_pain}",
            )
        )
        fig.update_xaxes(
            range=[min_strike, max_strike],
            constrain="domain",
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=60, b=20),
            template=cfg.PLT_SCAT_STYLE_TEMPLATE,
            title=f"Open Interest for {ticker.upper()} expiring {expiry}",
            title_x=0.5,
            legend_title="",
            xaxis_title="Strike",
            yaxis_title="Open Interest (1k)",
            xaxis=dict(
                rangeslider=dict(visible=False),
            ),
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
            dragmode="pan",
        )
        config = dict({"scrollZoom": True})
        imagefile = "opt_oi.png"

        # Check if interactive settings are enabled
        plt_link = ""
        if cfg.INTERACTIVE:
            html_ran = random.randint(69, 69420)
            fig.write_html(f"in/cci_{html_ran}.html", config=config)
            plt_link = f"[Interactive]({cfg.INTERACTIVE_URL}/cci_{html_ran}.html)"

        fig.update_layout(
            width=800,
            height=500,
        )
        fig.write_image(imagefile)

        img = Image.open(imagefile)
        im_bg = Image.open(cfg.IMG_BG)
        h = img.height + 240
        w = img.width + 520

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
            print(f"Image URL: {imagefile}")
        title = f"Open Interest for {ticker.upper()} expiring {expiry}"
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
            title="ERROR Options: Open Interest",
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
