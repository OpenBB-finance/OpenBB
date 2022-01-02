import difflib
import logging
import os
import sys
from datetime import datetime

import discord
import discord_components
import pyimgur

import config_discordbot as cfg

# Logging
logger = logging.getLogger("discord")
logging.basicConfig(level=logging.INFO)  # DEBUG/INFO/WARNING/ERROR/CRITICAL
handler = logging.FileHandler(
    filename=os.path.join(
        os.path.dirname(__file__), "..", "logs", f"{datetime.now()}_bot.log"
    ),
    encoding="utf-8",
    mode="w",
)
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)


activity = discord.Game(
    name="Gamestonk Terminal: https://github.com/GamestonkTerminal/GamestonkTerminal"
)


class GSTHelpCommand(discord.ext.commands.MinimalHelpCommand):
    """Custom Help Command."""

    def get_command_signature(self, command):
        command_syntax = f"{self.clean_prefix}{command.qualified_name}"
        command_usage = command.usage if command.usage is not None else ""
        signature_text = f"""
        Example usage:
            `{command_syntax} {command_usage}`"""
        return signature_text

    def add_bot_commands_formatting(self, commands, heading):
        """Add a minified bot heading with commands to the output."""
        if commands:
            menu_header = heading.replace("Commands", " category")
            self.paginator.add_line(
                f"__**{menu_header}**__ " + f"contains {len(commands)} commands."
            )
            self.paginator.add_line(f"\t\t`!help {heading}` for info and options.")


gst_bot = discord.ext.commands.Bot(
    command_prefix=cfg.COMMAND_PREFIX,
    help_command=GSTHelpCommand(sort_commands=False, commands_heading="list:"),
    intents=discord.Intents.all(),
    activity=activity,
)
discord_components.DiscordComponents(gst_bot)

if cfg.IMGUR_CLIENT_ID == "REPLACE_ME" or cfg.DISCORD_BOT_TOKEN == "REPLACE_ME":
    print(
        "Update IMGUR_CLIENT_ID or DISCORD_BOT_TOKEN or both in "
        + f"{ os.path.join('discordbot', 'config_discordbot') } \n"
    )
    sys.exit()


async def on_ready():
    print("GST Discord Bot Ready to Gamestonk!")


gst_imgur = pyimgur.Imgur(cfg.IMGUR_CLIENT_ID)

# Loads the commands (Cogs) from each "context"
gst_bot.load_extension("generic_commands")
gst_bot.load_extension("economy.economy_menu")
gst_bot.load_extension("stocks.dark_pool_shorts.dps_menu")
gst_bot.load_extension("stocks.technical_analysis.ta_menu")
gst_bot.load_extension("stocks.due_diligence.dd_menu")
gst_bot.load_extension("stocks.government.gov_menu")
gst_bot.load_extension("stocks.screener.screener_menu")
gst_bot.load_extension("stocks.options.options_menu")


# Get all command names
all_cmds = gst_bot.all_commands.keys()

# In case the user inserts a wrong command we check for similarity with
# available commands, and if there is we suggest one, otherwise we
# report list of all commands available


@gst_bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.CommandNotFound):
        cmd = str(error).split('"')[1]
        similar_cmd = difflib.get_close_matches(cmd, all_cmds, n=1, cutoff=0.7)

        if similar_cmd:
            error_help = f"Did you mean '**!{similar_cmd[0]}**'?"
        else:
            # TODO: This can be improved by triggering help menu
            error_help = f"**Possible commands are:** {', '.join(all_cmds)}"

        await ctx.send(f"_{error}_\n{error_help}\n")


# Runs the bot
gst_bot.run(cfg.DISCORD_BOT_TOKEN)
