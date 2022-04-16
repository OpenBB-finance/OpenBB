import hashlib
import logging
import platform
import traceback
import uuid
from typing import Any, Dict

import disnake
from disnake.ext import commands

from bots import config_discordbot as cfg
from openbb_terminal.decorators import log_start_end
from openbb_terminal.loggers import setup_logging

logger = logging.getLogger(__name__)
setup_logging("bot-app")
logger.info("START")
logger.info("Python: %s", platform.python_version())
logger.info("OS: %s", platform.system())

activity = disnake.Activity(
    type=disnake.ActivityType.watching,
    name="OpenBB Terminal: https://github.com/OpenBB-finance/OpenBBTerminal",
)


class _MissingSentinel:
    def __eq__(self, other):
        return False

    def __bool__(self):
        return False

    def __repr__(self):
        return "..."


MISSING: Any = _MissingSentinel()


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
            sync_commands_debug=True,
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
