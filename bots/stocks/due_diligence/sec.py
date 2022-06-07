import logging

from bots import config_discordbot as cfg
from openbb_terminal.decorators import log_start_end
from openbb_terminal.stocks.due_diligence import marketwatch_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def sec_command(ticker=""):
    """Displays sec filings [Market Watch]"""

    # Debug user input
    if cfg.DEBUG:
        logger.debug("dd sec %s", ticker)

    if ticker == "":
        raise Exception("A ticker is required")

    df_financials = marketwatch_model.get_sec_filings(ticker)

    if df_financials.empty:
        raise Exception("Enter a valid ticker")

    # Debug user output
    if cfg.DEBUG:
        logger.debug(df_financials.to_string())

    df = df_financials
    df.loc[:, "Link"] = "[Link Source](" + df.loc[:, "Link"].astype(str)
    df.loc[:, "Link"] = df.loc[:, "Link"] + ")"

    # Output data
    return {
        "title": "Stocks: [Market Watch] SEC Filings",
        "description": df.to_string(),
    }
