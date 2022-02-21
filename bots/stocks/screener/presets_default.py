import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from bots.stocks.screener import screener_options as so


def presets_default_command():
    """Displays default presets"""

    # Debug
    if cfg.DEBUG:
        logger.debug("scr-presets")

    description = ""
    for signame, sigdesc in so.d_signals_desc.items():
        description += f"**{signame}:** *{sigdesc}*\n"

    return {
        "title": "Stocks: Screener Default Presets",
        "description": description,
    }
