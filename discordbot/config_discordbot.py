import os
import sys
import discord

from dotenv import load_dotenv

env_files = [f for f in os.listdir() if f.endswith(".env")]
if env_files:
    load_dotenv(env_files[0])

# Relative path to the terminal
sys.path.append("..")

# DiscordBot https://discord.com/developers/applications/
DISCORD_BOT_TOKEN = (
    os.getenv("GT_DISCORD_BOT_TOKEN")
    or "OTA0NzYyNjEwODI0NjU0ODg4.YYAP2A.AmHf8NROAiPrOOKpmUR9g0wwvIc"
)

# https://apidocs.imgur.com
IMGUR_CLIENT_ID = os.getenv("GT_IMGUR_CLIENT_ID") or "623a199299858e7"


# Settings
COMMAND_PREFIX = "!"
DATE_FORMAT = "%Y-%m-%d"
COLOR = discord.Color.from_rgb(0, 206, 154)
MENU_TIMEOUT = 30
DEBUG = False

GST_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

AUTHOR_NAME = "Gamestonk Terminal"
AUTHOR_ICON_URL = (
    "https://github.com/GamestonkTerminal/GamestonkTerminal/"
    "blob/main/images/gst_logo_green_white_background.png?raw=true"
)
