import df2img
import disnake
from PIL import Image

import discordbot.config_discordbot as cfg
from discordbot.config_discordbot import logger
from discordbot.helpers import autocrop_image
from gamestonk_terminal.stocks.options import barchart_model


async def iv_command(ctx, ticker: str = None):
    """Options IV"""

    try:
        # Debug
        if cfg.DEBUG:
            logger.debug("!stocks.opt.iv %s", ticker)

        # Check for argument
        if ticker is None:
            raise Exception("Stock ticker is required")

        df = barchart_model.get_options_info(ticker)
        df = df.fillna("")
        df = df.set_axis(
            [
                " ",
                "",
            ],
            axis="columns",
        )
        df.set_index(" ", inplace=True)
        fig = df2img.plot_dataframe(
            df,
            fig_size=(600, 1500),
            col_width=[3, 3],
            tbl_cells=dict(
                align="left",
                height=35,
            ),
            template="plotly_dark",
            font=dict(
                family="Consolas",
                size=20,
            ),
            paper_bgcolor="rgba(0, 0, 0, 0)",
        )
        imagefile = "opt-iv.png"
        df2img.save_dataframe(fig=fig, filename=imagefile)
        image = Image.open(imagefile)
        image = autocrop_image(image, 0)
        image.save(imagefile, "PNG", quality=100)
        image = disnake.File(imagefile)
        title = f"{ticker.upper()} Options: IV"
        embed = disnake.Embed(title=title, colour=cfg.COLOR)
        embed.set_image(url=f"attachment://{imagefile}")
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        await ctx.send(embed=embed, file=image)

    except Exception as e:
        embed = disnake.Embed(
            title="ERROR Options: IV",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
