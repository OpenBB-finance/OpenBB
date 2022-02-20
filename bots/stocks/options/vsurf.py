import numpy as np
import plotly.graph_objects as go
from scipy.spatial import Delaunay

import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from bots import helpers
from gamestonk_terminal.stocks.options import yfinance_model


def vsurf_command(
    ticker: str = "",
    z: str = "IV",
):
    """Display vol surface

    Parameters
    ----------
    ticker: Stock Ticker
    z : The variable for the Z axis
    """

    # Debug
    if cfg.DEBUG:
        logger.debug("opt-oi %s %s", ticker, z)

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

    # Check if interactive settings are enabled
    plt_link = ""
    if cfg.INTERACTIVE:
        html_ran = helpers.uuid_get()
        fig.write_html(f"in/vsurf_{html_ran}.html", config=config)
        plt_link = f"[Interactive]({cfg.INTERACTIVE_URL}/vsurf_{html_ran}.html)"

    fig.update_layout(
        width=800,
        height=500,
    )

    imagefile = helpers.image_border(imagefile, fig=fig)

    return {
        "title": f"{label} Surface for {ticker.upper()}",
        "description": plt_link,
        "imagefile": imagefile,
    }
