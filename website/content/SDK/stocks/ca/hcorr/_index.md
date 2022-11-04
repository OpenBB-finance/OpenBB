To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.ca.hcorr(similar: List[str], start_date: str = '2021-11-03', candle_type: str = 'a')


    Get historical price correlation. [Source: Yahoo Finance]

    Parameters
    ----------
    similar : List[str]
        List of similar tickers.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().
    start_date : str, optional
        Start date of comparison, by default 1 year ago
    candle_type : str, optional
        OHLCA column to use for candles or R for returns, by default "a" for Adjusted Close

## Getting charts 
### stocks.ca.hcorr(similar: List[str], start_date: str = '2021-11-03', candle_type: str = 'a', display_full_matrix: bool = False, raw: bool = False, external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, export: str = '', chart=True)


    Correlation heatmap based on historical price comparison
    between similar companies. [Source: Yahoo Finance]

    Parameters
    ----------
    similar : List[str]
        List of similar tickers.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().
    start_date : str, optional
        Start date of comparison, by default 1 year ago
    candle_type : str, optional
        OHLCA column to use for candles or R for returns, by default "a" for Adjusted Close
    display_full_matrix : bool, optional
        Optionally display all values in the matrix, rather than masking off half, by default False
    raw: bool, optional
        Whether to display raw data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    export : str, optional
        Format to export correlation prices, by default ""
