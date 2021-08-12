"""Tradingview view"""
__docformat__ = "numpy"


from gamestonk_terminal.stocks.technical_analysis import tradingview_model


def print_recommendation(ticker: str, screener: str, exchange: str, interval: str):
    """Print tradingview recommendation based on technical indicators

    Parameters
    ----------
    ticker : str
        Ticker to get tradingview recommendation based on technical indicators
    screener : str
        Screener based on tradingview docs https://python-tradingview-ta.readthedocs.io/en/latest/usage.html
    exchange: str
        Exchange based on tradingview docs https://python-tradingview-ta.readthedocs.io/en/latest/usage.html
    interval: str
        Interval time to check technical indicators and correspondent recommendation
    """

    recom = tradingview_model.get_tradingview_recommendation(
        ticker, screener, exchange, interval
    )
    print(recom, "\n")
