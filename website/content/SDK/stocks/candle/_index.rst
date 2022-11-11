.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.candle(
    symbol: str,
    data: pandas.core.frame.DataFrame = None,
    use_matplotlib: bool = True,
    intraday: bool = False,
    add_trend: bool = False,
    ma: Optional[Iterable[int]] = None,
    asset_type: str = '',
    start_date: Union[datetime.datetime, str, NoneType] = None,
    interval: int = 1440,
    end_date: Union[datetime.datetime, str, NoneType] = None,
    prepost: bool = False,
    source: str = 'YahooFinance',
    iexrange: str = 'ytd',
    weekly: bool = False,
    monthly: bool = False,
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    raw: bool = False,
    yscale: str = 'linear',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Show candle plot of loaded ticker.

    [Source: Yahoo Finance, IEX Cloud or Alpha Vantage]
    </p>

* **Parameters**

    symbol: str
        Ticker name
    data: pd.DataFrame
        Stock dataframe
    use_matplotlib: bool
        Flag to use matplotlib instead of interactive plotly chart
    intraday: bool
        Flag for intraday data for plotly range breaks
    add_trend: bool
        Flag to add high and low trends to chart
    ma: Tuple[int]
        Moving averages to add to the candle
    asset_type\_: str
        String to include in title
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    asset_type\_: str
        String to include in title
    start_date: str or datetime, optional
        Start date to get data from with. - datetime or string format (YYYY-MM-DD)
    interval: int
        Interval (in minutes) to get data 1, 5, 15, 30, 60 or 1440
    end_date: str or datetime, optional
        End date to get data from with. - datetime or string format (YYYY-MM-DD)
    prepost: bool
        Pre and After hours data
    source: str
        Source of data extracted
    iexrange: str
        Timeframe to get IEX data.
    weekly: bool
        Flag to get weekly data
    monthly: bool
        Flag to get monthly data
    raw : bool, optional
        Flag to display raw data, by default False
    yscale: str
        Linear or log for yscale
