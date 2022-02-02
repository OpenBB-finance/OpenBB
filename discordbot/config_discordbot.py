from typing import List
import logging
import os
import sys

import disnake
import pyimgur

from dotenv import load_dotenv

env_files = [f for f in os.listdir() if f.endswith(".env")]
if env_files:
    load_dotenv(env_files[0])

# Logging
logger = logging.getLogger("discord")
logging.basicConfig(level=logging.INFO)  # DEBUG/INFO/WARNING/ERROR/CRITICAL
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)

# Relative path to the terminal
sys.path.append("..")

# https://discord.com/developers/applications/
DISCORD_BOT_TOKEN = os.getenv("GT_DISCORD_BOT_TOKEN") or "REPLACE_ME"

# https://apidocs.imgur.com
IMGUR_CLIENT_ID = os.getenv("GT_IMGUR_CLIENT_ID") or "REPLACE_ME"

# Settings
SLASH_TESTING_SERVERS: List[int] = []  # Test server IDs
COMMAND_PREFIX = "!"
DATE_FORMAT = "%Y-%m-%d"
COLOR = disnake.Color.from_rgb(255, 0, 0)
INTERACTIVE = False
INTERACTIVE_URL = ""
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
PLT_TBL_STYLE_TEMPLATE = "plotly_dark"
PLT_TBL_CELLS = dict(
    height=35,
)
PLT_TBL_FONT = dict(
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
