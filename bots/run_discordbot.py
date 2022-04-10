# pylint: skip-file
import asyncio
import hashlib
import logging
import os
import platform
import sys
import traceback
import uuid
from pathlib import Path
from typing import Any, Dict

import disnake
from disnake.ext import commands
from fastapi import FastAPI, Request

try:
    from bots import config_discordbot as cfg
except ImportError:
    sys.path.append(Path(__file__).parent.parent.resolve().__str__())
    from bots import config_discordbot as cfg
finally:
    from bots.groupme.run_groupme import handle_groupme
    from openbb_terminal.decorators import log_start_end
    from openbb_terminal.loggers import setup_logging

logger = logging.getLogger(__name__)
setup_logging(f"bot_pid_{os.getpid()}")
logger.info("START")
logger.info("Python: %s", platform.python_version())
logger.info("OS: %s", platform.system())

app = FastAPI()


class _MissingSentinel:
    def __eq__(self, other):
        return False

    def __bool__(self):
        return False

    def __repr__(self):
        return "..."


MISSING: Any = _MissingSentinel()


@app.get("/")
async def read_root():
    return {"Hello": str(openbb_bot.user)}


@app.post("/")
async def write_root(request: Request):
    # TODO: Make this work for more bots
    req_info = await request.body()
    value = handle_groupme(req_info)
    return {"Worked": value}


activity = disnake.Activity(
    type=disnake.ActivityType.watching,
    name="OpenBB Terminal: https://github.com/OpenBB-finance/OpenBBTerminal",
)


def hash_user_id(user_id: str) -> str:
    hash_object = hashlib.new("md4", user_id.encode("utf-8"))
    return str(uuid.UUID(hash_object.hexdigest(), version=4))


def fancy_traceback(exc: Exception) -> str:
    """May not fit the message content limit"""
    text = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    return f"```py\n{text[-4086:]}\n```"


@log_start_end(log=logger)
class GSTBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=cfg.COMMAND_PREFIX,
            intents=disnake.Intents.all(),
            help_command=None,  # type: ignore
            sync_commands_debug=False,
            sync_permissions=True,
            activity=activity,
            test_guilds=cfg.SLASH_TESTING_SERVERS,
        )

    def load_all_extensions(self, folder: str) -> None:
        folder_path = cfg.bots_path.joinpath(folder)
        for name in folder_path.iterdir():
            if name.__str__().endswith(".py") and name.is_file():
                self.load_extension(f"{folder}.{name.stem}")

    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.CheckAnyFailure):
            await ctx.message.delete()

    async def on_application_command_autocomplete(
        self,
        inter: disnake.AppCmdInter,
    ) -> None:
        if inter.response._responded:
            pass
        else:
            if inter.response._responded:
                pass
            else:
                await self.process_app_command_autocompletion(inter)

    async def on_slash_command_error(
        self,
        inter: disnake.AppCmdInter,
        error: commands.CommandError,
    ) -> None:
        if inter.response._responded:
            pass
        else:
            if isinstance(error, commands.NoPrivateMessage):
                logger.info("Slash No Private Message Error")
                tickred = "<a:tickred:942466341082902528>"
                embed = disnake.Embed(
                    title="Command Execution Error",
                    color=disnake.Color.red(),
                    description=f"{tickred}  This command cannot be used in private messages!",
                )
                if inter.response._responded:
                    pass
                else:
                    await inter.response.send_message(embed=embed, ephemeral=True)
            elif isinstance(error, commands.MissingPermissions):
                logger.info("Slash Permissions Error")
                tickred = "<a:tickred:942466341082902528>"
                embed = disnake.Embed(
                    title="Command Execution Error",
                    color=disnake.Color.red(),
                    description=f"{tickred} You do not have enough permissions to execute this command!",
                )
                if inter.response._responded:
                    pass
                else:
                    await inter.response.send_message(embed=embed, ephemeral=True)
            elif isinstance(error, commands.CheckAnyFailure):
                logger.info("Slash Permissions Error")
                tickred = "<a:tickred:942466341082902528>"
                embed = disnake.Embed(
                    title="Command Execution Error",
                    color=0xF00,
                    description=f"{tickred} You do not have enough permissions to execute this command!",
                )
                if inter.response._responded:
                    pass
                else:
                    await inter.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = disnake.Embed(
                    title="",
                    description=f"Slash command `{inter.data.name}` failed due to `{error}`\n{fancy_traceback(error)}",
                    color=disnake.Color.red(),
                )
                if inter.response._responded:
                    pass
                else:
                    await inter.response.send_message(embed=embed, ephemeral=True)

    async def on_application_command(
        self,
        inter: disnake.AppCmdInter,
    ) -> None:
        if inter.response._responded:
            pass
        else:
            await self.process_application_commands(inter)
            if inter.filled_options is MISSING:
                filled: Dict[str, Any] = {"N/A": ""}
            else:
                filled = inter.filled_options
            if inter.data.name is MISSING:
                cmd_name: str = ""
            else:
                cmd_name = inter.data.name
            if inter.guild:
                server: Any[Dict[str, Any]] = {
                    "guild_id": inter.guild.id,
                    "name": inter.guild.name,
                    "channel": inter.channel.name,
                    "member_count": inter.guild.member_count,
                }
            else:
                server = "DM"

            stats_log = {
                "data": [
                    {
                        "server": server,
                        "command": {
                            "name": cmd_name,
                            "cmd_data": filled,
                        },
                    }
                ],
            }

            log_uid = {"user_id": hash_user_id(str(inter.author.id))}
            logger.info(stats_log, extra=log_uid)

            pass

    async def on_user_command_error(
        self,
        inter: disnake.AppCmdInter,
        error: commands.CommandError,
    ) -> None:
        if inter.response._responded:
            pass
        else:
            embed = disnake.Embed(
                title="",
                description=f"User command `{inter.data.name}` failed due to `{error}`\n{fancy_traceback(error)}",
                color=disnake.Color.red(),
            )
            if inter.response._responded:
                pass
            else:
                await inter.response.send_message(embed=embed, ephemeral=True)

    async def on_message_command_error(
        self,
        inter: disnake.AppCmdInter,
        error: commands.CommandError,
    ) -> None:
        if inter.response._responded:
            pass
        else:
            embed = disnake.Embed(
                title="",
                description=f"Message command `{inter.data.name}` failed due to `{error}`\n{fancy_traceback(error)}",
                color=disnake.Color.red(),
            )
            if inter.response._responded:
                pass
            else:
                await inter.response.send_message(embed=embed, ephemeral=True)

    async def on_ready(self):
        # fmt: off
        guildname = []
        for guild in self.guilds:
            guildname.append(guild.name)
        members = []
        for guild in self.guilds:
            for member in guild.members:
                members.append(member)

        dindex = len(members)
        logger.info(
            "Servers connected to:"
            f"{guildname}"
            f"Total members: {dindex}"
        )
        logger.info(
            f"The bot is ready."
            f"User: {self.user}"
            f"ID: {self.user.id}"
        )
        # fmt: on


if cfg.IMGUR_CLIENT_ID == "REPLACE_ME" or cfg.DISCORD_BOT_TOKEN == "REPLACE_ME":
    logger.info(
        "Update IMGUR_CLIENT_ID or DISCORD_BOT_TOKEN or both in %s \n",
        os.path.join("discordbot", "config_discordbot"),
    )
    sys.exit()
print(f"disnake: {disnake.__version__}\n")


openbb_bot = GSTBot()
openbb_bot.load_all_extensions("cmds")


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
