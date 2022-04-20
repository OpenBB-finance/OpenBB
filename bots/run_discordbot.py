# pylint: skip-file
import asyncio
import logging
import os
import sys
from pathlib import Path

import disnake
from disnake.ext import commands
from fastapi import FastAPI, Request


try:
    from bots import config_discordbot as cfg
except ImportError:
    sys.path.append(Path(__file__).parent.parent.resolve().__str__())
    from bots import config_discordbot as cfg
finally:
    from bots.discord import helpers
    from bots.groupme.run_groupme import handle_groupme

logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": str(openbb_bot.user)}


@app.post("/")
async def write_root(request: Request):
    # TODO: Make this work for more bots
    req_info = await request.body()
    value = handle_groupme(req_info)
    return {"Worked": value}


if cfg.IMGUR_CLIENT_ID == "REPLACE_ME" or cfg.DISCORD_BOT_TOKEN == "REPLACE_ME":
    logger.info(
        "Update IMGUR_CLIENT_ID or DISCORD_BOT_TOKEN or both in %s \n",
        os.path.join("discordbot", "config_discordbot"),
    )
    sys.exit()
print(f"disnake: {disnake.__version__}\n")


openbb_bot = helpers.GSTBot()
openbb_bot.load_all_extensions("cmds")


@openbb_bot.slash_command()
@commands.guild_only()
@commands.has_permissions(manage_messages=True)
async def support(inter: disnake.CommandInteraction):
    """Send support ticket! *Mods Only"""
    await inter.response.send_modal(modal=MyModal())


@openbb_bot.slash_command()
async def stats(
    self,
    inter: disnake.AppCmdInter,
):
    """Bot Stats"""
    guildname = []
    for guild in openbb_bot.guilds:
        guildname.append(guild.name)
    members = []
    for guild in openbb_bot.guilds:
        for member in guild.members:
            members.append(member)
    embed = disnake.Embed(
        title="Bot Stats",
        colour=cfg.COLOR,
    )
    embed.add_field(
        name="Servers",
        value=f"```css\n{len(guildname):^20}\n```",
        inline=False,
    )
    embed.add_field(
        name="Users",
        value=f"```css\n{len(members):^20}\n```",
        inline=False,
    )

    await inter.send(embed=embed)


@app.on_event("startup")
async def startup_event():
    try:
        asyncio.create_task(openbb_bot.start(cfg.DISCORD_BOT_TOKEN))
    except KeyboardInterrupt:
        await openbb_bot.logout()


class MyModal(disnake.ui.Modal):
    def __init__(self) -> None:
        components = [
            disnake.ui.TextInput(
                label="Issue",
                placeholder="_ _",
                custom_id="issue",
                style=disnake.TextInputStyle.short,
                min_length=5,
                max_length=50,
            ),
            disnake.ui.TextInput(
                label="Image",
                placeholder="Url to an image showing error",
                custom_id="image",
                style=disnake.TextInputStyle.short,
                min_length=5,
                max_length=500,
            ),
            disnake.ui.TextInput(
                label="Description",
                placeholder="Please specify what command and inputs gave the error",
                custom_id="description",
                style=disnake.TextInputStyle.paragraph,
                min_length=5,
                max_length=1024,
            ),
        ]
        super().__init__(
            title="Support Ticket", custom_id="support_ticket", components=components
        )

    async def callback(self, inter: disnake.ModalInteraction) -> None:
        embed = disnake.Embed(title="Support Ticket")
        channel = await openbb_bot.fetch_channel(943929570002878514)
        embed.add_field(name="User", value=inter.author.name, inline=True)
        embed.add_field(name="Server", value=inter.guild.name, inline=True)  # type: ignore
        embed.add_field(name="Issue", value=inter.text_values["issue"], inline=False)
        embed.add_field(
            name="Description", value=inter.text_values["description"], inline=False
        )
        embed.set_image(url=inter.text_values["image"])
        await inter.response.send_message("Ticket Sent. Thank you!!", ephemeral=True)
        await channel.send(embed=embed)

    async def on_error(self, error: Exception, inter: disnake.ModalInteraction) -> None:
        await inter.response.send_message("Oops, something went wrong.", ephemeral=True)
