import logging

import bots.config_discordbot as cfg
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.stocks.due_diligence import csimarket_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def supplier_command(ticker=""):
    """Displays suppliers of the company [CSIMarket]"""

    # Debug user input
    if cfg.DEBUG:
        logger.debug("dd supplier %s", ticker)

    if not ticker:
        raise Exception("A ticker is required")

    tickers = csimarket_model.get_suppliers(ticker)

    if not tickers:
        raise Exception("Enter a valid ticker")

    # Debug user output
    if cfg.DEBUG:
        logger.debug(tickers)

    # Output data
    return {
        "title": "Stocks: [CSIMarket] Company Suppliers",
        "description": tickers,
    }
