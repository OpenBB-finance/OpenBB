import os
import random
import time

import disnake
import numpy as np
import plotly.graph_objects as go
from PIL import Image
from scipy.spatial import Delaunay

import discordbot.config_discordbot as cfg
from discordbot.helpers import autocrop_image
from gamestonk_terminal.stocks.options import yfinance_model

startTime = time.time()


async def vsurf_command(
    ctx,
    ticker: str = "",
    z: str = "IV",
):
    """Display vol surface

    Parameters
    ----------
    ticker: Stock Ticker
    z : The variable for the Z axis
    """
    try:

        # Debug
        print(f"!stocks.opt.oi {ticker} {z}")

        # Check for argument
        if ticker == "":
            raise Exception("Stock ticker is required")

        data = yfinance_model.get_iv_surface(ticker)
        if data.empty:
            raise Exception(f"No options data found for {ticker}.\n")

        Y = data.dte
        X = data.strike
        if z == "IV":
            Z = data.impliedVolatility
            label = "Volatility"
        elif z == "OI":
            Z = data.openInterest
            label = "Open Interest"
        elif z == "LP":
            Z = data.lastPrice
            label = "Last Price"

        points3D = np.vstack((X, Y, Z)).T
        points2D = points3D[:, :2]
        tri = Delaunay(points2D)
        I, J, K = tri.simplices.T

        lighting_effects = dict(
            ambient=0.5, diffuse=0.5, roughness=0.5, specular=0.4, fresnel=0.4
        )
        fig = go.Figure(
            data=[
                go.Mesh3d(
                    z=Z,
                    x=X,
                    y=Y,
                    i=I,
                    j=J,
                    k=K,
                    intensity=Z,
                    colorscale=cfg.PLT_3DMESH_COLORSCALE,
                    hovertemplate="<b>DTE</b>: %{y} <br><b>Strike</b>: %{x} <br><b>"
                    + z
                    + "</b>: %{z}<extra></extra>",
                    showscale=False,
                    flatshading=True,
                    lighting=lighting_effects,
                )
            ]
        )
        fig.update_layout(
            scene=dict(
                xaxis=dict(
                    title="Strike",
                    tickfont=dict(size=11),
                    titlefont=dict(size=12),
                ),
                yaxis=dict(
                    title="DTE",
                ),
                zaxis=dict(
                    title=z,
                ),
            ),
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=40, b=20),
            width=1320,
            height=740,
            template=cfg.PLT_3DMESH_STYLE_TEMPLATE,
            title=f"{label} Surface for {ticker.upper()}",
            title_x=0.5,
            hoverlabel=cfg.PLT_3DMESH_HOVERLABEL,
            scene_camera=dict(
                up=dict(x=0, y=0, z=2),
                center=dict(x=0, y=0, z=-0.3),
                eye=dict(x=1.25, y=1.25, z=0.69),
            ),
            scene=cfg.PLT_3DMESH_SCENE,
        )
        config = dict({"scrollZoom": True})
        imagefile = "opt-vsurf.png"
        fig.write_image(imagefile)

        # Check if interactive settings are enabled
        plt_link = ""
        if cfg.INTERACTIVE:
            html_ran = random.randint(69, 69420)
            fig.write_html(f"in/vsurf_{html_ran}.html", config=config)
            plt_link = f"[Interactive]({cfg.INTERACTIVE_URL}/vsurf_{html_ran}.html)"

        img = Image.open(imagefile)
        im_bg = Image.open(cfg.IMG_BG)
        h = img.height
        w = img.width

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
        title = f"{label} Surface for {ticker.upper()}"
        embed = disnake.Embed(title=title, description=plt_link, colour=cfg.COLOR)
        embed.set_image(url=f"attachment://{imagefile}")
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        os.remove(imagefile)

        await ctx.send(embed=embed, file=image)

    except IndexError:
        embed = disnake.Embed(
            title="ERROR Options: Volatility Surface",
            colour=cfg.COLOR,
            description=f"Inconistent data for {ticker.upper()} {z}",
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)

    except Exception as e:
        embed = disnake.Embed(
            title="ERROR Options: Volatility Surface",
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
