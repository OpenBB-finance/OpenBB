To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.dd.eb(symbol: str, exchange: str = 'binance', start_date: int = 1262322000, end_date: int = 1667592183) -> pandas.core.frame.DataFrame

Returns the total amount of coins held on exchange addresses in units and percentage.
    [Source: https://glassnode.com]

    Parameters
    ----------
    symbol : str
        Asset to search active addresses (e.g., BTC)
    exchange : str
        Exchange to check net position change (e.g., binance)
    start_date : int
        Initial date timestamp (e.g., 1_614_556_800)
    end_date : int
        End date timestamp (e.g., 1_614_556_800)

    Returns
    -------
    pd.DataFrame
        total amount of coins in units/percentage and symbol price over time

## Getting charts 
### crypto.dd.eb(symbol: str, exchange: str = 'binance', start_date: int = 1577836800, end_date: int = 1609459200, percentage: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> None

Display total amount of coins held on exchange addresses in units and percentage.
    [Source: https://glassnode.org]

    Parameters
    ----------
    symbol : str
        Asset to search active addresses (e.g., BTC)
    exchange : str
        Exchange to check net position change (possible values are: aggregated, binance, bittrex,
        coinex, gate.io, gemini, huobi, kucoin, poloniex, bibox, bigone, bitfinex, hitbtc, kraken,
        okex, bithumb, zb.com, cobinhood, bitmex, bitstamp, coinbase, coincheck, luno)
    start_date : int
        Initial date timestamp (e.g., 1_614_556_800)
    end_date : int
        End date timestamp (e.g., 1_614_556_800)
    percentage : bool
        Show percentage instead of stacked value.
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
