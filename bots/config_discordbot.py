import logging
import os
import sys
from typing import List, Optional

import disnake
import pyimgur
from dotenv import load_dotenv

from gamestonk_terminal.loggers import setup_logging

env_files = [f for f in os.listdir() if f.endswith(".env")]
if env_files:
    load_dotenv(env_files[0])

# Logging
logger = logging.getLogger(__name__)
setup_logging()


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
INTERACTIVE_URL = ""
IMG_DIR = "in/images"
IMAGES_URL = ""
# IMG_BG = "files/bg.png"  # Light BG
IMG_BG = "files/bg-dark.png"  # Dark BG
PLT_3DMESH_COLORSCALE = "Jet"
PLT_3DMESH_SCENE = dict(
    xaxis=dict(
        backgroundcolor="rgb(94, 94, 94)",
        gridcolor="white",
        showbackground=True,
        zerolinecolor="white",
    ),
    yaxis=dict(
        backgroundcolor="rgb(94, 94, 94)",
        gridcolor="white",
        showbackground=True,
        zerolinecolor="white",
    ),
    zaxis=dict(
        backgroundcolor="rgb(94, 94, 94)",
        gridcolor="white",
        showbackground=True,
        zerolinecolor="white",
    ),
    aspectratio=dict(x=1.2, y=1.2, z=0.8),
)
PLT_3DMESH_HOVERLABEL = dict(bgcolor="gold")
PLT_3DMESH_STYLE_TEMPLATE = "plotly_dark"
PLT_CANDLE_STYLE_TEMPLATE = "plotly_dark"
PLT_SCAT_STYLE_TEMPLATE = "plotly_dark"
PLT_TA_STYLE_TEMPLATE = "plotly_dark"
PLT_TA_COLORWAY = [
    "#fdc708",
    "#d81aea",
    "#00e6c3",
    "#9467bd",
    "#e250c3",
    "#d1fa3d",
]
PLT_TBL_HEADER = dict(
    fill_color="rgb(30, 30, 30)",
    font_color="white",
    line_color="rgb(63, 63, 63)",
    line_width=2,
)
PLT_TBL_CELLS = dict(
    height=35,
    fill_color="rgb(50, 50, 50)",
    font_color="white",
    line_color="rgb(63, 63, 63)",
    line_width=2,
)
PLT_TBL_FONT = dict(
    family="Consolas",
    size=20,
)
PLT_FONT = dict(
    family="Consolas",
    size=20,
)
MENU_TIMEOUT = 30
DEBUG = False

GST_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

gst_imgur = pyimgur.Imgur(IMGUR_CLIENT_ID)

AUTHOR_NAME = "Gamestonk Terminal"
AUTHOR_URL = "https://github.com/GamestonkTerminal/GamestonkTerminal"
AUTHOR_ICON_URL = (
    "https://github.com/GamestonkTerminal/GamestonkTerminal/"
    "blob/main/images/gst_logo_green_white_background.png?raw=true"
)
