# common.behavioural_analysis.sentiment_stats

To specify a view add `chart=True` as the last parameter

## Model (ticker: str) -> Dict

Get sentiment stats [Source: finnhub]

    Parameters
    ----------
    ticker : str
        Ticker to get sentiment stats

    Returns
    -------
    Dict
        Get sentiment stats

## View (ticker: str, export: str = '')


    Sentiment stats which displays buzz, news score, articles last week, articles weekly average,
    bullish vs bearish percentages, sector average bullish percentage, and sector average news score

    Parameters
    ----------
    ticker : str
        Ticker to get sentiment stats
    export : str
        Format to export data
