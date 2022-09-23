## Get underlying data 
### stocks.disc.ford() -> Tuple[str, pandas.core.frame.DataFrame]

Returns Fidelity orders in a Dataframe

    Returns
    -------
    Tuple[str, DataFrame]
        First value in the tuple is a Fidelity orders header
        Fidelity orders Dataframe with the following columns:
        Symbol, Buy / Sell Ratio, Price Change, Company, # Buy Orders, # Sell Orders
