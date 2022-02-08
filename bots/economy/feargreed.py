import datetime
import os

import disnake
import matplotlib.pyplot as plt

import discordbot.config_discordbot as cfg
from discordbot.config_discordbot import gst_imgur, logger
from gamestonk_terminal.economy import cnn_model, cnn_view


async def feargreed_command(ctx, indicator=""):
    """CNN Fear and Greed Index [CNN]"""

    try:
        # Debug user input
        if cfg.DEBUG:
            logger.debug("econ-futures")

        # Check for argument
        possible_indicators = ("", "jbd", "mv", "pco", "mm", "sps", "spb", "shd")

        if indicator not in possible_indicators:
            raise Exception(
                f"Select a valid indicator from {', '.join(possible_indicators)}"  # nosec
            )

        # Retrieve data
        fig = plt.figure(figsize=[1, 1], dpi=10)

        report, _ = cnn_model.get_feargreed_report(indicator, fig)
        cnn_view.fear_and_greed_index(indicator=indicator, export="png")
        plt.close("all")

        # Output data
        now = datetime.datetime.now()
        image_path = os.path.join(
            cfg.GST_PATH,
            "exports",
            "economy",
            f"feargreed_{now.strftime('%Y%m%d_%H%M%S')}.png",
        )

        i = 0
        while not os.path.exists(image_path) and i < 10:
            now -= datetime.timedelta(seconds=1)
            image_path = os.path.join(
                cfg.GST_PATH,
                "exports",
                "economy",
                f"feargreed_{now.strftime('%Y%m%d_%H%M%S')}.png",
            )
            i += 1

        embed = disnake.Embed(
            title="Economy: [CNN] Fear Geed Index",
            description=report,
            colour=cfg.COLOR,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        if os.path.exists(image_path):
            uploaded_image = gst_imgur.upload_image(
                image_path, title="FearGreed Charts"
            )
            embed.set_image(url=uploaded_image.link)

        else:
            logger.error("Error when uploading the the image to Imgur.")

        await ctx.send(embed=embed)

    except Exception as e:
        logger.error("ERROR Economy: [CNN] Feargreed. %s", e)
        embed = disnake.Embed(
            title="ERROR Economy: [CNN] Feargreed",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
