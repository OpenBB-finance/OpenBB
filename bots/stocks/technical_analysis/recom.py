import logging

from bots import config_discordbot as cfg
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.stocks.technical_analysis import tradingview_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def recom_command(ticker=""):
    """Displays text of a given stocks recommendation based on ta [Tradingview API]"""

    # Debug
    if cfg.DEBUG:
        logger.debug("ta recom %s", ticker)

    # Check for argument
    if ticker == "":
        raise Exception("Stock ticker is required")

    recom = tradingview_model.get_tradingview_recommendation(ticker, "america", "", "")

    recom = recom[["BUY", "NEUTRAL", "SELL", "RECOMMENDATION"]]

    report = "```" + recom.to_string() + "```"

    return {
        "title": "Stocks: [Tradingview API] Recommendation based on TA",
        "description": report,
    }
