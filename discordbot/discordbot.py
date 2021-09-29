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


async def on_ready():
    print("GST Discord Bot Ready to Gamestonk!")


gst_imgur = pyimgur.Imgur(cfg.IMGUR_CLIENT_ID)

# Loads the commands (Cogs) from each "context"
gst_bot.load_extension("generic_commands")
gst_bot.load_extension("economy.economy_menu")
gst_bot.load_extension("stocks.dark_pool_shorts.dps_menu")

# Runs the bot
gst_bot.run(cfg.DISCORD_BOT_TOKEN)
