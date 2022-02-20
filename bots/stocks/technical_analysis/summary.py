import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from gamestonk_terminal.stocks.technical_analysis import finbrain_model


def summary_command(ticker=""):
    """Displays text of a given stocks ta summary [FinBrain API]"""

    # Debug
    if cfg.DEBUG:
        logger.debug("ta-summary %s", ticker)

    # Check for argument
    if ticker == "":
        raise Exception("Stock ticker is required")

    report = finbrain_model.get_technical_summary_report(ticker)
    if report:
        report = "```" + report.replace(". ", ".\n") + "```"

    return {
        "title": "Stocks: [FinBrain API] Summary",
        "description": report,
    }
