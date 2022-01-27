import datetime
import os

import discord
import matplotlib.pyplot as plt

import discordbot.config_discordbot as cfg


class BotController:
    async def discord(self, gst_imgur, logger, func, ctx, *args, **kwargs):
        # Output data
        try:
            data = func(*args, **kwargs)
            now = datetime.datetime.now()
            image_path = os.path.join(
                cfg.GST_PATH,
                "exports",
                data["mid_path"],
                f"{data['name']}_{now.strftime('%Y%m%d_%H%M%S')}.png",
            )

            i = 0
            while not os.path.exists(image_path) and i < 10:
                now -= datetime.timedelta(seconds=1)
                image_path = os.path.join(
                    cfg.GST_PATH,
                    "exports",
                    data["mid_path"],
                    f"{data['name']}_{now.strftime('%Y%m%d_%H%M%S')}.png",
                )
                i += 1

            plt.close("all")

            embed = discord.Embed(
                title=data["title"],
                description=data["report"],
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
            logger.error("ERROR %s. %s", {data["title"]}, e)
            embed = discord.Embed(
                title=f"ERROR {data['title']}",
                colour=cfg.COLOR,
                description=e,
            )
            embed.set_author(
                name=cfg.AUTHOR_NAME,
                icon_url=cfg.AUTHOR_ICON_URL,
            )

            await ctx.send(embed=embed)


bot_controller = BotController()
