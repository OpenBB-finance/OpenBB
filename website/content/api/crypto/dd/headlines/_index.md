To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.dd.headlines(symbol: str) -> pandas.core.frame.DataFrame

Gets Sentiment analysis provided by FinBrain's API [Source: finbrain]

    Parameters
    ----------
    symbol : str
        Ticker symbol to get the sentiment analysis from

    Returns
    -------
    DataFrame()
        Empty if there was an issue with data retrieval

## Getting charts 
### crypto.dd.headlines(symbol: str, raw: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> None

Sentiment analysis from FinBrain for Cryptocurrencies

    FinBrain collects the news headlines from 15+ major financial news
    sources on a daily basis and analyzes them to generate sentiment scores
    for more than 4500 US stocks. FinBrain Technologies develops deep learning
    algorithms for financial analysis and prediction, which currently serves
    traders from more than 150 countries all around the world.
    [Source:  https://finbrain.tech]

    Parameters
    ----------
    symbol: str
        Cryptocurrency
    raw : False
        Display raw table data
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
