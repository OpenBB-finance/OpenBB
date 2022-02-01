import os

import df2img
import discordbot.config_discordbot as cfg
import disnake
from discordbot.config_discordbot import gst_imgur, logger
from discordbot.helpers import autocrop_image
from gamestonk_terminal.stocks.discovery import seeking_alpha_model
from PIL import Image
from menus.menu import Menu


async def earnings_command(ctx):
    """Display Upcoming Earnings. [Source: Seeking Alpha]
    """

    try:
        # Debug
        if cfg.DEBUG:
            logger.debug("earnings")

        df_earnings = seeking_alpha_model.get_next_earnings(1)
        for n_days, earning_date in enumerate(df_earnings.index.unique()):

            df_earn = df_earnings[earning_date == df_earnings.index][
                ["Ticker", "Name"]
            ].dropna()

            df_earn.index = df_earn["Ticker"].values
            df_earn.drop(columns=["Ticker"], inplace=True)

        title = f"Earnings on {earning_date.date()}"

        embeds: list = []
        # Weekly Calls Pages
        i, i2, end = 0, 0, 20
        df_pg = []
        embeds_img = []
        dindex = len(df_earn.index)
        while i < dindex:
            df_pg = df_earn.iloc[i:end]
            df_pg.append(df_pg)
            figp = df2img.plot_dataframe(
                df_pg,
                fig_size=(800, (40 + (40 * dindex))),
                col_width=[1, 5],
                tbl_cells=dict(
                    align=["center", "left"],
                    height=35,
                ),
                template="plotly_dark",
                font=dict(
                    family="Consolas",
                    size=20,
                ),
                paper_bgcolor="rgba(0, 0, 0, 0)",
            )
            imagefile = f"disc-upcoming{i}.png"

            df2img.save_dataframe(fig=figp, filename=imagefile)
            image = Image.open(imagefile)
            image = autocrop_image(image, 0)
            image.save(imagefile, "PNG", quality=100)

            uploaded_image = gst_imgur.upload_image(imagefile, title="something")
            image_link = uploaded_image.link
            embeds_img.append(
                f"{image_link}",
            )
            embeds.append(
                disnake.Embed(
                    title=title,
                    colour=cfg.COLOR,
                ),
            )
            i2 += 1
            i += 20
            end += 20
            os.remove(imagefile)

        # Author/Footer
        for i in range(0, i2):
            embeds[i].set_author(
                name=cfg.AUTHOR_NAME,
                url=cfg.AUTHOR_URL,
                icon_url=cfg.AUTHOR_ICON_URL,
            )
            embeds[i].set_footer(
                text=cfg.AUTHOR_NAME,
                icon_url=cfg.AUTHOR_ICON_URL,
            )

        i = 0
        for i in range(0, i2):
            embeds[i].set_image(url=embeds_img[i])

            i += 1
        embeds[0].set_footer(text=f"Page 1 of {len(embeds)}")
        options = [
            disnake.SelectOption(label="Home", value="0", emoji="🟢"),
        ]

        await ctx.send(embed=embeds[0], view=Menu(embeds, options))

    except Exception as e:
        embed = disnake.Embed(
            title="ERROR Display Upcoming Earnings.",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
