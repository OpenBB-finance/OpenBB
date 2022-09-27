To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.options.info(symbol: str)

Get info for a given ticker

    Parameters
    ----------
    symbol : str
        The ticker symbol to get the price for

    Returns
    ----------
    price : float
        The info for a given ticker

## Getting charts 
### stocks.options.info(symbol: str, export: str = '', chart=True)

Scrapes Barchart.com for the options information

    Parameters
    ----------
    symbol: str
        Ticker symbol to get options info for
    export: str
        Format of export file
