import os
import sys
from pathlib import Path
from typing import List, Optional

import disnake
import pyimgur
from dotenv import load_dotenv

# Path to bots
bots_path = Path(__file__).parent.absolute()

env_files = [f for f in bots_path.iterdir() if f.as_posix().endswith(".env")]

if env_files:
    load_dotenv(env_files[0])

# Relative path to the terminal
sys.path.append("..")

# https://discord.com/developers/applications/
DISCORD_BOT_TOKEN = os.getenv("GT_DISCORD_BOT_TOKEN") or "REPLACE_ME"

# https://apidocs.imgur.com
IMGUR_CLIENT_ID = os.getenv("GT_IMGUR_CLIENT_ID") or "REPLACE_ME"

# https://newsapi.org
API_NEWS_TOKEN = os.getenv("GT_API_NEWS_TOKEN") or "REPLACE_ME"

# https://www.binance.com/en/
API_BINANCE_KEY = os.getenv("GT_API_BINANCE_KEY") or "REPLACE_ME"
API_BINANCE_SECRET = os.getenv("GT_API_BINANCE_SECRET") or "REPLACE_ME"

# https://finnhub.io
API_FINNHUB_KEY = os.getenv("GT_API_FINNHUB_KEY") or "REPLACE_ME"

# Settings
SLASH_TESTING_SERVERS: Optional[
    List[int]
] = None  # Add server ID for testing [1884912191119489, 1454644614118448]
COMMAND_PREFIX = "!"
DATE_FORMAT = "%Y-%m-%d"
COLOR = disnake.Color.from_rgb(255, 0, 0)
INTERACTIVE = False
INTERACTIVE_DIR = bots_path / "interactive/"
INTERACTIVE_URL = ""
IMG_DIR = bots_path / "interactive/images/"
IMAGES_URL = ""  # Ex. "http://your-site.com/images/"

# IMG_BG = bots_path.joinpath("files/bg.png")  # Light BG
IMG_BG = bots_path.joinpath("files/bg-dark.png")  # Dark BG

MENU_TIMEOUT = 30
DEBUG = False

GST_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

gst_imgur = pyimgur.Imgur(IMGUR_CLIENT_ID) if IMGUR_CLIENT_ID != "REPLACE_ME" else None

AUTHOR_NAME = "Gamestonk Terminal"
AUTHOR_URL = "https://github.com/GamestonkTerminal/GamestonkTerminal"
AUTHOR_ICON_URL = (
    "https://github.com/GamestonkTerminal/GamestonkTerminal/"
    "blob/main/images/gst_logo_green_white_background.png?raw=true"
)
