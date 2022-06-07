import os
from distutils.util import strtobool
from pathlib import Path
from typing import List, Optional

import disnake
import pyimgur
from dotenv import load_dotenv

# Path to bots
bots_path = Path(__file__).parent.resolve()
GST_PATH = Path(__file__).parent.parent.resolve()

env_files = [f for f in bots_path.iterdir() if f.__str__().endswith(".env")]

if env_files:
    load_dotenv(env_files[0])

# https://discord.com/developers/applications/
DISCORD_BOT_TOKEN = os.getenv("OPENBB_DISCORD_BOT_TOKEN") or "REPLACE_ME"

# https://apidocs.imgur.com
IMGUR_CLIENT_ID = os.getenv("OPENBB_IMGUR_CLIENT_ID") or "REPLACE_ME"

# https://newsapi.org
API_NEWS_TOKEN = os.getenv("OPENBB_API_NEWS_TOKEN") or "REPLACE_ME"

# https://www.binance.com/en/
API_BINANCE_KEY = os.getenv("OPENBB_API_BINANCE_KEY") or "REPLACE_ME"
API_BINANCE_SECRET = os.getenv("OPENBB_API_BINANCE_SECRET") or "REPLACE_ME"

# https://stocksera.pythonanywhere.com/accounts/developers/
API_STOCKSERA_TOKEN = os.getenv("OPENBB_API_STOCKSERA_TOKEN") or "REPLACE_ME"

# https://finnhub.io
API_FINNHUB_KEY = os.getenv("OPENBB_API_FINNHUB_KEY") or "REPLACE_ME"

# Settings
SLASH_TESTING_SERVERS: Optional[
    List[int]
] = None  # Add server ID for testing [1884912191119489, 1454644614118448]
COMMAND_PREFIX = "!"
DATE_FORMAT = "%Y-%m-%d"
COLOR = disnake.Color.from_rgb(130, 38, 97)

# Interactive Chart Settings
INTERACTIVE = strtobool(os.getenv("OPENBB_INTERACTIVE", "False"))
INTERACTIVE_DIR = (
    Path(str(os.getenv("OPENBB_INTERACTIVE_DIR")))
    if os.getenv("OPENBB_INTERACTIVE_DIR")
    else bots_path.joinpath("interactive/")
)
INTERACTIVE_URL = os.getenv("OPENBB_INTERACTIVE_URL") or ""

# Image Settings
IMG_HOST_ACTIVE = strtobool(os.getenv("OPENBB_IMG_HOST_ACTIVE", "False"))
IMG_DIR = (
    Path(str(os.getenv("OPENBB_IMG_DIR")))
    if os.getenv("OPENBB_IMG_DIR")
    else bots_path.joinpath("interactive/images/")
)
IMAGES_URL = os.getenv("OPENBB_IMAGES_URL") or ""  # Ex. "http://your-site.com/images/"

# IMG_BG = bots_path.joinpath("files/bg.png")  # Light BG
IMG_BG = bots_path.joinpath("files/bg-dark_openbb.png")  # Dark BG

DEBUG = strtobool(os.getenv("OPENBB_DEBUG", "False"))

openbb_imgur = pyimgur.Imgur(IMGUR_CLIENT_ID)

AUTHOR_NAME = "OpenBB Bot"
AUTHOR_URL = "https://github.com/OpenBB-finance/OpenBBTerminal"
AUTHOR_ICON_URL = (
    "https://raw.githubusercontent.com/OpenBB-finance/OpenBBTerminal/"
    "hugo_rename/images/openbb_logo.png"
)
