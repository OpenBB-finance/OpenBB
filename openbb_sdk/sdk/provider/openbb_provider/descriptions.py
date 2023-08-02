"""Common descriptions for model fields."""

QUERY_DESCRIPTIONS = {
    "symbol": "Symbol to get data for.",
    "start_date": "Start date of the data, in YYYY-MM-DD format.",
    "end_date": "End date of the data, in YYYY-MM-DD format.",
    "weekly": "Whether to return weekly data.",
    "monthly": "Whether to return monthly data.",
    "period": "Period of the data to return.",
    "date": "A specific date to get data for.",
    "limit": "The number of data entries to return.",
    "countries": "The country or countries to get data.",
    "units": "The data units.",
    "frequency": "The data time frequency.",
}

DATA_DESCRIPTIONS = {
    "symbol": "Symbol representing the entity requested in the data.",
    "date": "The date of the data.",
    "open": "The open price of the symbol.",
    "high": "The high price of the symbol.",
    "low": "The low price of the symbol.",
    "close": "The close price of the symbol.",
    "volume": "The volume of the symbol.",
    "adj_close": "The adjusted close price of the symbol.",
    "vwap": "Volume Weighted Average Price of the symbol.",
}
