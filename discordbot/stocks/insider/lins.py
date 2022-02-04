import os

import df2img
import disnake
import pandas as pd
from menus.menu import Menu
from PIL import Image

import discordbot.config_discordbot as cfg
from discordbot.config_discordbot import gst_imgur, logger
from discordbot.helpers import autocrop_image
from gamestonk_terminal.stocks.insider import finviz_model


async def lins_command(ctx, ticker: str = "", num: int = 10):
    """Display insider activity for a given stock ticker. [Source: Finviz]

    Parameters
    ----------
    ticker : Stock Ticker
    num : Number of latest insider activity to display
    """
    try:
        # Debug
        if cfg.DEBUG:
            logger.debug("disc-lins %s", num)

        d_finviz_insider = finviz_model.get_last_insider_activity(ticker)

        df = pd.DataFrame.from_dict(d_finviz_insider)
        df.set_index("Date", inplace=True)

        df = df[
            [
                "Relationship",
                "Transaction",
                "#Shares",
                "Cost",
                "Value ($)",
                "#Shares Total",
                "Insider Trading",
                "SEC Form 4",
            ]
        ]

        df = df.head(num)
        df = df.replace(to_replace="Option Exercise", value="Opt Ex.", regex=True)

        title = f"Insider Trading for {ticker.upper()}"

        embeds: list = []

        i, i2, end = 0, 0, 20
        df_pg = []
        embeds_img = []
        dindex = len(df.index)
        while i < dindex:
            df_pg = df.iloc[i:end]
            df_pg.append(df_pg)
            fig = df2img.plot_dataframe(
                df_pg,
                fig_size=(1600, (40 + (40 * 20))),
                col_width=[5, 14, 4, 4, 3, 4, 5, 8, 7],
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
            imagefile = f"disc-insider{i}.png"

            df2img.save_dataframe(fig=fig, filename=imagefile)
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
            title="ERROR Insider Activity [Source: Finviz]",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
