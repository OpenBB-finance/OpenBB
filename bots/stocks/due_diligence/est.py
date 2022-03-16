import logging
import os

import df2img
import disnake

import bots.config_discordbot as cfg
from bots.config_discordbot import gst_imgur
from bots.helpers import save_image
from bots.menus.menu import Menu
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.stocks.due_diligence import business_insider_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def est_command(ticker: str = ""):
    """Displays earning estimates [Business Insider]"""

    # Debug
    if cfg.DEBUG:
        logger.debug("dd est %s", ticker)

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

    images_list = []
    dindex = len(df_year_estimates.index)
    fig = df2img.plot_dataframe(
        df_year_estimates,
        fig_size=(900, (40 + (60 * dindex))),
        col_width=[9, 4, 4, 4, 4],
        tbl_header=cfg.PLT_TBL_HEADER,
        tbl_cells=cfg.PLT_TBL_CELLS,
        font=cfg.PLT_TBL_FONT,
        row_fill_color=cfg.PLT_TBL_ROW_COLORS,
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )
    imagefile = save_image("estimates.png", fig)

    if cfg.IMAGES_URL or cfg.IMGUR_CLIENT_ID != "REPLACE_ME":
        link_estimates = cfg.IMAGES_URL + imagefile
        images_list.append(imagefile)
    else:
        imagefile_save = cfg.IMG_DIR / imagefile
        uploaded_image = gst_imgur.upload_image(imagefile_save, title="something")
        link_estimates = uploaded_image.link
        os.remove(imagefile_save)

    fig = df2img.plot_dataframe(
        df_quarter_earnings,
        fig_size=(900, (40 + (40 * 20))),
        col_width=[5, 5, 4, 4, 5, 4],
        tbl_header=cfg.PLT_TBL_HEADER,
        tbl_cells=cfg.PLT_TBL_CELLS,
        font=cfg.PLT_TBL_FONT,
        row_fill_color=cfg.PLT_TBL_ROW_COLORS,
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )
    imagefile = save_image("earnings.png", fig)

    if cfg.IMAGES_URL or cfg.IMGUR_CLIENT_ID != "REPLACE_ME":
        link_earnings = cfg.IMAGES_URL + imagefile
        images_list.append(imagefile)
    else:
        imagefile_save = cfg.IMG_DIR / imagefile
        uploaded_image = gst_imgur.upload_image(imagefile_save, title="something")
        link_earnings = uploaded_image.link
        os.remove(imagefile_save)

    fig = df2img.plot_dataframe(
        df_quarter_revenues,
        fig_size=(900, (40 + (40 * 20))),
        col_width=[5, 5, 4, 4, 5, 4],
        tbl_header=cfg.PLT_TBL_HEADER,
        tbl_cells=cfg.PLT_TBL_CELLS,
        font=cfg.PLT_TBL_FONT,
        row_fill_color=cfg.PLT_TBL_ROW_COLORS,
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )
    imagefile = save_image("revenues.png", fig)

    if cfg.IMAGES_URL or cfg.IMGUR_CLIENT_ID != "REPLACE_ME":
        link_revenues = cfg.IMAGES_URL + imagefile
        images_list.append(imagefile)
    else:
        imagefile_save = cfg.IMG_DIR / imagefile
        uploaded_image = gst_imgur.upload_image(imagefile_save, title="something")
        link_revenues = uploaded_image.link
        os.remove(imagefile_save)

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
        "images_list": images_list,
    }
