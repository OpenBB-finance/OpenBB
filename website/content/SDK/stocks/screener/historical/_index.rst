.. role:: python(code)
    :language: python
    :class: highlight

|

To obtain charts, make sure to add :python:`chart = True` as the last parameter.

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.screener.historical(
    preset_loaded: str = 'top_gainers',
    limit: int = 10,
    start_date: str = '2022-05-18',
    type_candle: str = 'a',
    normalize: bool = True,
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, List[str], bool]
{{< /highlight >}}

.. raw:: html

    <p>
    View historical price of stocks that meet preset
    </p>

* **Parameters**

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
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Dataframe of the screener
    list[str]
        List of stocks
    bool
        Whether some random stock selection due to limitations

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.screener.historical(
    preset_loaded: str = 'top_gainers',
    limit: int = 10,
    start_date: str = '2022-05-18',
    type_candle: str = 'a',
    normalize: bool = True,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
) -> List[str]
{{< /highlight >}}

.. raw:: html

    <p>
    View historical price of stocks that meet preset
    </p>

* **Parameters**

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
    chart: bool
       Flag to display chart


* **Returns**

    list[str]
        List of stocks
