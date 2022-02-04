import os

import df2img
import disnake
from PIL import Image

import discordbot.config_discordbot as cfg
from discordbot.config_discordbot import logger
from discordbot.helpers import autocrop_image
from gamestonk_terminal.stocks.discovery import fidelity_model


async def ford_command(ctx):
    """Display Orders by Fidelity Customers. [Source: Fidelity]

    Parameters
    ----------
    num: Number of stocks to display
    """

    try:
        # Debug
        if cfg.DEBUG:
            logger.debug("!ford")
        order_header, df_orders = fidelity_model.get_orders()

        df_orders = df_orders.head(n=30).iloc[:, :-1]
        df_orders = df_orders.applymap(str)

        font_color = (
            ["white"] * 2
            + [
                [
                    "#ad0000" if boolv else "#0d5700"
                    for boolv in df_orders["Price Change"].str.contains("-")
                ]
            ]
            + [["white"] * 3]
        )

        df_orders.set_index("Symbol", inplace=True)
        df_orders = df_orders.apply(lambda x: x.str.slice(0, 20))

        dindex = len(df_orders.index)
        fig = df2img.plot_dataframe(
            df_orders,
            fig_size=(1500, (40 + (40 * dindex))),
            col_width=[1, 3, 2.2, 3, 2, 2],
            tbl_cells=dict(
                align=["left", "center", "left", "left", "center"],
                font=dict(color=font_color),
                height=35,
            ),
            template="plotly_dark",
            font=dict(
                family="Consolas",
                size=20,
            ),
            paper_bgcolor="rgba(0, 0, 0, 0)",
        )
        imagefile = "disc-ford.png"
        df2img.save_dataframe(fig=fig, filename=imagefile)

        image = Image.open(imagefile)
        image = autocrop_image(image, 0)
        image.save(imagefile, "PNG", quality=100)

        image = disnake.File(imagefile)

        title = "Fidelity Customer Orders"
        embed = disnake.Embed(title=title, colour=cfg.COLOR)
        embed.set_image(url=f"attachment://{imagefile}")
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        os.remove(imagefile)

        await ctx.send(embed=embed, file=image)

    except Exception as e:
        embed = disnake.Embed(
            title="ERROR Fidelity Customer Orders",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
