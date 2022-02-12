import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from bots.stocks.screener import screener_options as so


def presets_custom_command():
    """Displays every custom preset"""

    # Debug
    if cfg.DEBUG:
        logger.debug("scr-presets")

    description = ""
    for preset in so.presets:
        with open(
            so.presets_path + preset + ".ini",
            encoding="utf8",
        ) as f:
            preset_line = ""
            for line in f:
                if line.strip() == "[General]":
                    break
                preset_line += line.strip()
        description += f"**{preset}:** *{preset_line.split('Description: ')[1].replace('#', '')}*\n"

    return {
        "title": "Stocks: Screener Custom Presets",
        "description": description,
    }
