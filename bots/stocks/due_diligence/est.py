import logging
import os

import disnake

from bots import imps
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.stocks.due_diligence import business_insider_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def est_command(ticker: str = ""):
    """Displays earning estimates [Business Insider]"""

    # Debug
    if imps.DEBUG:
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
    if imps.DEBUG:
        logger.debug(df_year_estimates.to_string())
        logger.debug(df_quarter_earnings.to_string())
        logger.debug(df_quarter_revenues.to_string())

    images_list = []
    dindex = len(df_year_estimates.index)
    fig = imps.plot_df(
        df_year_estimates,
        fig_size=(900, (40 + (60 * dindex))),
        col_width=[9, 4, 4, 4, 4],
        tbl_header=imps.PLT_TBL_HEADER,
        tbl_cells=imps.PLT_TBL_CELLS,
        font=imps.PLT_TBL_FONT,
        row_fill_color=imps.PLT_TBL_ROW_COLORS,
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )
    imagefile = imps.save_image("estimates.png", fig)

    if imps.IMAGES_URL or imps.IMGUR_CLIENT_ID != "REPLACE_ME":
        link_estimates = imps.IMAGES_URL + imagefile
        images_list.append(imagefile)
    else:
        imagefile_save = imps.IMG_DIR / imagefile
        uploaded_image = imps.gst_imgur.upload_image(imagefile_save, title="something")
        link_estimates = uploaded_image.link
        os.remove(imagefile_save)

    fig = imps.plot_df(
        df_quarter_earnings,
        fig_size=(900, (40 + (40 * 20))),
        col_width=[5, 5, 4, 4, 5, 4],
        tbl_header=imps.PLT_TBL_HEADER,
        tbl_cells=imps.PLT_TBL_CELLS,
        font=imps.PLT_TBL_FONT,
        row_fill_color=imps.PLT_TBL_ROW_COLORS,
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )
    imagefile = imps.save_image("earnings.png", fig)

    if imps.IMAGES_URL or imps.IMGUR_CLIENT_ID != "REPLACE_ME":
        link_earnings = imps.IMAGES_URL + imagefile
        images_list.append(imagefile)
    else:
        imagefile_save = imps.IMG_DIR / imagefile
        uploaded_image = imps.gst_imgur.upload_image(imagefile_save, title="something")
        link_earnings = uploaded_image.link
        os.remove(imagefile_save)

    fig = imps.plot_df(
        df_quarter_revenues,
        fig_size=(900, (40 + (40 * 20))),
        col_width=[5, 5, 4, 4, 5, 4],
        tbl_header=imps.PLT_TBL_HEADER,
        tbl_cells=imps.PLT_TBL_CELLS,
        font=imps.PLT_TBL_FONT,
        row_fill_color=imps.PLT_TBL_ROW_COLORS,
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )
    imagefile = imps.save_image("revenues.png", fig)

    if imps.IMAGES_URL or imps.IMGUR_CLIENT_ID != "REPLACE_ME":
        link_revenues = imps.IMAGES_URL + imagefile
        images_list.append(imagefile)
    else:
        imagefile_save = imps.IMG_DIR / imagefile
        uploaded_image = imps.gst_imgur.upload_image(imagefile_save, title="something")
        link_revenues = uploaded_image.link
        os.remove(imagefile_save)

    embeds = [
        disnake.Embed(
            title=f"**{ticker.upper()} Year Estimates**",
            color=imps.COLOR,
        ),
        disnake.Embed(
            title=f"**{ticker.upper()} Quarter Earnings**",
            colour=imps.COLOR,
        ),
        disnake.Embed(
            title=f"**{ticker.upper()} Quarter Revenues**",
            colour=imps.COLOR,
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
        "view": imps.Menu,
        "titles": titles,
        "embed": embeds,
        "choices": choices,
        "embeds_img": embeds_img,
        "images_list": images_list,
    }
