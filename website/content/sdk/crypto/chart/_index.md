To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.chart(prices_df: 'pd.DataFrame', to_symbol: 'str' = '', from_symbol: 'str' = '', source: 'str' = '', exchange: 'str' = '', interval: 'str' = '', external_axes: 'list[plt.Axes] | None' = None, yscale: 'str' = 'linear') -> 'None'

Load data for Technical Analysis

    Parameters
    ----------
    prices_df: pd.DataFrame
        Cryptocurrency
    to_symbol: str
        Coin (only used for chart title), by default ""
    from_symbol: str
        Currency (only used for chart title), by default ""
    yscale: str
        Scale for y axis of plot Either linear or log

## Getting charts 
### crypto.chart(prices_df: 'pd.DataFrame', to_symbol: 'str' = '', from_symbol: 'str' = '', source: 'str' = '', exchange: 'str' = '', interval: 'str' = '', external_axes: 'list[plt.Axes] | None' = None, yscale: 'str' = 'linear', chart=True) -> 'None'

Load data for Technical Analysis

    Parameters
    ----------
    prices_df: pd.DataFrame
        Cryptocurrency
    to_symbol: str
        Coin (only used for chart title), by default ""
    from_symbol: str
        Currency (only used for chart title), by default ""
    yscale: str
        Scale for y axis of plot Either linear or log
