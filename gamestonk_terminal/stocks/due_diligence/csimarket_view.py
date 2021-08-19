"""CSIMarket View"""
__docformat__ = "numpy"

from gamestonk_terminal.stocks.due_diligence import csimarket_model


def suppliers(ticker: str):
    """Print suppliers from ticker provided. [Source: CSIMarket]

    Parameters
    ----------
    ticker: str
        Ticker to select suppliers from
    """
    print(csimarket_model.get_suppliers(ticker))


def customers(ticker: str):
    """Print customers from ticker provided. [Source: CSIMarket]

    Parameters
    ----------
    ticker: str
        Ticker to select customers from
    """
    print(csimarket_model.get_customers(ticker))
