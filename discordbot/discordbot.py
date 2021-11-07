import os
import sys
import difflib
import discord
import discord_components
import pyimgur
import config_discordbot as cfg


activity = discord.Game(
    name="Gametonk Terminal: https://github.com/GamestonkTerminal/GamestonkTerminal"
)

gst_bot = discord.ext.commands.Bot(
    command_prefix=cfg.COMMAND_PREFIX, intents=discord.Intents.all(), activity=activity
)
discord_components.DiscordComponents(gst_bot)

if cfg.IMGUR_CLIENT_ID == "REPLACE_ME" or cfg.DISCORD_BOT_TOKEN == "REPLACE_ME":
    print(
        f"Update IMGUR_CLIENT_ID or DISCORD_BOT_TOKEN or both in { os.path.join('discordbot', 'config_discordot') } \n"
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
