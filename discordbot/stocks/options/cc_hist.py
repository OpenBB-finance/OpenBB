import os
import random
import time

import disnake
import plotly.graph_objects as go
import yfinance as yf
from PIL import Image
from plotly.subplots import make_subplots

import discordbot.config_discordbot as cfg
from discordbot.helpers import autocrop_image

startTime = time.time()


async def cc_hist_command(
    ctx, ticker: str = None, expiry: str = "", strike: float = 10, opt_type: str = ""
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
        title = f"\n{ticker.upper()} {strike} {opt_type} expiring {expiry} Historical"

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
            "green" if row.Open < row["Close"] else "red"
            for _, row in df_hist.iterrows()  # pylint: disable=E1120
        ]
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
        rand = random.randint(69, 69420)
        imagefile = f"opt_hist{rand}.png"
        fig.write_image(imagefile)

        # Check if interactive settings are enabled
        plt_link = ""
        if cfg.INTERACTIVE:
            fig.write_html(f"in/cc_hist_{rand}.html", config=config)
            plt_link = f"[Interactive]({cfg.INTERACTIVE_URL}/cc_hist_{rand}.html)"

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
