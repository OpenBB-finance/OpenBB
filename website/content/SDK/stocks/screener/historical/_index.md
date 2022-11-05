To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.screener.historical(preset_loaded: str = 'top_gainers', limit: int = 10, start_date: str = '2022-05-07', type_candle: str = 'a', normalize: bool = True)

View historical price of stocks that meet preset

    Parameters
    ----------
    preset_loaded: str
        Preset loaded to filter for tickers
    limit: int
        Number of stocks to display
    start_date: str
        Start date to display historical data, in YYYY-MM-DD format
    type_candle: str
        Type of candle to display
    normalize : bool
        Boolean to normalize all stock prices using MinMax

    Returns
    -------
    pd.DataFrame
        Dataframe of the screener
    list[str]
        List of stocks
    bool
        Whether some random stock selection due to limitations

## Getting charts 
### stocks.screener.historical(preset_loaded: str = 'top_gainers', limit: int = 10, start_date: str = '2022-05-07', type_candle: str = 'a', normalize: bool = True, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> List[str]

View historical price of stocks that meet preset

    Parameters
    ----------
    preset_loaded: str
        Preset loaded to filter for tickers
    limit: int
        Number of stocks to display
    start_date: str
        Start date to display historical data, in YYYY-MM-DD format
    type_candle: str
        Type of candle to display
    normalize : bool
        Boolean to normalize all stock prices using MinMax
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

    Returns
    -------
    list[str]
        List of stocks
