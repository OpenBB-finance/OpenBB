import os
import datetime
import matplotlib.pyplot as plt
import discord

from gamestonk_terminal.economy import cnn_view, cnn_model
import discordbot.config_discordbot as cfg
from discordbot.run_discordbot import gst_imgur


async def feargreed_command(ctx, indicator=""):
    """CNN Fear and Greed Index [CNN]"""

    try:
        # Debug user input
        if cfg.DEBUG:
            print(f"\n!economy.feargreed {indicator}")

        # Check for argument
        possible_indicators = ("", "jbd", "mv", "pco", "mm", "sps", "spb", "shd")

        if indicator not in possible_indicators:
            raise Exception(
                f"Select a valid indicator from {', '.join(possible_indicators)}"
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

        embed = discord.Embed(
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
            if cfg.DEBUG:
                print("Error with uploading the the image to Imgur.")

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Economy: [CNN] Feargreed",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
