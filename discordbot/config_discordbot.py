import os
import sys
import discord

from dotenv import load_dotenv

env_files = [f for f in os.listdir() if f.endswith(".env")]
if env_files:
    load_dotenv(env_files[0])

# Relative path to the terminal
sys.path.append("..")

DISCORD_BOT_TOKEN = "ODg2NTQ0NTkxODQ1NzQwNTQ0.YT3I_Q.hkCmX06jCnZtl0mtgLhXvwvasJs"

IMGUR_CLIENT_ID = "2c6ae1b42387fba"

# Settings
COMMAND_PREFIX = "!"
DATE_FORMAT = "%Y-%m-%d"
COLOR = discord.Color.from_rgb(0, 206, 154)
MENU_TIMEOUT = 30
DEBUG = True

AUTHOR_NAME = "Gamestonk Terminal"
AUTHOR_ICON_URL = (
    "https://github.com/GamestonkTerminal/GamestonkTerminal/"
    "blob/main/images/gst_logo_green_white_background.png?raw=true"
)
