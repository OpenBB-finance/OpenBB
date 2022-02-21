import os

import df2img
import disnake

import bots.config_discordbot as cfg
from bots.config_discordbot import gst_imgur, logger
from bots.helpers import save_image
from bots.menus.menu import Menu
from gamestonk_terminal.stocks.due_diligence import business_insider_model


def est_command(ticker: str = ""):
    """Displays earning estimates [Business Insider]"""

    # Debug
    if cfg.DEBUG:
        logger.debug("dd-est %s", ticker)

    # Check for argument
    if ticker == "":
        raise Exception("Stock ticker is required")

    (
        df_year_estimates,
        df_quarter_earnings,
        df_quarter_revenues,
    ) = business_insider_model.get_estimates(ticker)

    if (
        df_quarter_revenues.empty
        and df_year_estimates.empty
        and df_quarter_earnings.empty
    ):
        raise Exception("Enter a valid ticker")

    # Debug user output
    if cfg.DEBUG:
        logger.debug(df_year_estimates.to_string())
        logger.debug(df_quarter_earnings.to_string())
        logger.debug(df_quarter_revenues.to_string())

    dindex = len(df_year_estimates.index)
    fig = df2img.plot_dataframe(
        df_year_estimates,
        fig_size=(1200, (40 + (60 * dindex))),
        col_width=[12, 4, 4, 4, 4],
        tbl_cells=dict(
            height=35,
        ),
        font=dict(
            family="Consolas",
            size=20,
        ),
        template="plotly_dark",
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )
    imagefile = save_image("estimates.png", fig)

    uploaded_image = gst_imgur.upload_image(imagefile, title="something")
    link_estimates = uploaded_image.link

    os.remove(imagefile)

    fig = df2img.plot_dataframe(
        df_quarter_earnings,
        fig_size=(1200, (40 + (40 * 20))),
        col_width=[5, 5, 4, 4, 5, 4],
        tbl_cells=dict(
            height=35,
        ),
        font=dict(
            family="Consolas",
            size=20,
        ),
        template="plotly_dark",
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )
    imagefile = save_image("earnings.png", fig)

    uploaded_image = gst_imgur.upload_image(imagefile, title="something")
    link_earnings = uploaded_image.link
    os.remove(imagefile)

    fig = df2img.plot_dataframe(
        df_quarter_revenues,
        fig_size=(1200, (40 + (40 * 20))),
        col_width=[5, 5, 4, 4, 5, 4],
        tbl_cells=dict(
            height=35,
        ),
        font=dict(
            family="Consolas",
            size=20,
        ),
        template="plotly_dark",
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )
    imagefile = save_image("revenues.png", fig)

    uploaded_image = gst_imgur.upload_image(imagefile, title="something")
    link_revenues = uploaded_image.link
    os.remove(imagefile)

    embeds = [
        disnake.Embed(
            title=f"**{ticker.upper()} Year Estimates**",
            color=cfg.COLOR,
        ),
        disnake.Embed(
            title=f"**{ticker.upper()} Quarter Earnings**",
            colour=cfg.COLOR,
        ),
        disnake.Embed(
            title=f"**{ticker.upper()} Quarter Revenues**",
            colour=cfg.COLOR,
        ),
    ]
    embeds[0].set_image(url=link_estimates)
    embeds[1].set_image(url=link_earnings)
    embeds[2].set_image(url=link_revenues)
    titles = [
        f"**{ticker.upper()} Year Estimates**",
        f"**{ticker.upper()} Quarter Earnings**",
        f"**{ticker.upper()} Quarter Revenues**",
    ]
    embeds_img = [
        f"{link_estimates}",
        f"{link_earnings}",
        f"{link_revenues}",
    ]
    # Output data
    choices = [
        disnake.SelectOption(
            label=f"{ticker.upper()} Year Estimates", value="0", emoji="🟢"
        ),
        disnake.SelectOption(
            label=f"{ticker.upper()} Quarter Earnings", value="1", emoji="🟢"
        ),
        disnake.SelectOption(
            label=f"{ticker.upper()} Quarter Revenues", value="2", emoji="🟢"
        ),
    ]

    return {
        "view": Menu,
        "titles": titles,
        "embed": embeds,
        "choices": choices,
        "embeds_img": embeds_img,
    }
