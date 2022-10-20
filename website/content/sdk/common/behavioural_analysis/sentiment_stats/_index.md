# common.behavioural_analysis.sentiment_stats

To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
###common.behavioural_analysis.sentiment_stats(ticker: str) -> Dict

Get sentiment stats [Source: finnhub]

    Parameters
    ----------
    ticker : str
        Ticker to get sentiment stats

    Returns
    -------
    Dict
        Get sentiment stats

## Getting charts 
###common.behavioural_analysis.sentiment_stats(ticker: str, export: str = '', chart=True)


    Sentiment stats which displays buzz, news score, articles last week, articles weekly average,
    bullish vs bearish percentages, sector average bullish percentage, and sector average news score

    Parameters
    ----------
    ticker : str
        Ticker to get sentiment stats
    export : str
        Format to export data
