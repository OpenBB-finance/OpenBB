import logging

import bots.config_discordbot as cfg
from bots.stocks.screener import screener_options as so
from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
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
