## Get underlying data 
### crypto.price(symbol: str)

Returns price and confidence interval from pyth live feed. [Source: Pyth]

    Parameters
    ----------
    symbol : str
        Symbol of the asset to get price and confidence interval from

    Returns
    -------
    float
        Price of the asset
    float
        Confidence level
    float
        Previous price of the asset
