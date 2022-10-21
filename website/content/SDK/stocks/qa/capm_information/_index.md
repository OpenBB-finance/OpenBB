## Get underlying data 
### stocks.qa.capm_information(symbol: str) -> Tuple[float, float]

Provides information that relates to the CAPM model

    Parameters
    ----------
    symbol : str
        A ticker symbol in string form

    Returns
    -------
    beta : float
        The beta for a stock
    sys : float
        The systematic risk for a stock
