.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Shows candle plot of loaded ticker. [Source: Yahoo Finance, IEX Cloud or Alpha Vantage]
    </h3>

{{< highlight python >}}
stocks.candle(
    symbol: str,
    data: pandas.core.frame.DataFrame = None,
    use\_matplotlib: bool = True,
    intraday: bool = False,
    add\_trend: bool = False,
    ma: Optional[Iterable[int]] = None,
    asset\_type: str = '',
    start\_date: datetime.datetime = datetime.datetime(
    2019, 10, 26, 23, 20, 36, 878267, ), interval: int = 1440,
    end\_date: datetime.datetime = datetime.datetime(
    2022, 10, 30, 23, 20, 36, 878278, ), prepost: bool = False,
    source: str = 'YahooFinance',
    iexrange: str = 'ytd',
    weekly: bool = False,
    monthly: bool = False,
    external\_axes: Optional[List[matplotlib.axes.\_axes.Axes]] = None, raw: bool = False,
    yscale: str = 'linear',
    )
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Ticker name
    data: *pd.DataFrame*
        Stock dataframe
    use\_matplotlib: *bool*
        Flag to use matplotlib instead of interactive plotly chart
    intraday: *bool*
        Flag for intraday data for plotly range breaks
    add\_trend: *bool*
        Flag to add high and low trends to chart
    ma: Tuple[int]
        Moving averages to add to the candle
    asset\_type\_: *str*
        String to include in title
    external\_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    asset\_type\_: *str*
        String to include in title
    start\_date: *datetime*
        Start date to get data from with
    interval: *int*
        Interval (in minutes) to get data 1, 5, 15, 30, 60 or 1440
    end\_date: *datetime*
        End date to get data from with
    prepost: *bool*
        Pre and After hours data
    source: *str*
        Source of data extracted
    iexrange: *str*
        Timeframe to get IEX data.
    weekly: *bool*
        Flag to get weekly data
    monthly: *bool*
        Flag to get monthly data
    raw : bool, optional
        Flag to display raw data, by default False
    yscale: *str*
        Linear or log for yscale
    