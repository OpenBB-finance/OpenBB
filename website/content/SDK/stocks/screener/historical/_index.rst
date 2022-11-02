.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > View historical price of stocks that meet preset
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
stocks.screener.historical(
    preset_loaded: str = 'top_gainers',
    limit: int = 10,
    start_date: str = '2022-05-06',
    type_candle: str = 'a',
    normalize: bool = True,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
)
{{< /highlight >}}

* **Parameters**

    preset_loaded: *str*
        Preset loaded to filter for tickers
    limit: *int*
        Number of stocks to display
    start_date: *str*
        Start date to display historical data, in YYYY-MM-DD format
    type_candle: *str*
        Type of candle to display
    normalize : *bool*
        Boolean to normalize all stock prices using MinMax
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        Dataframe of the screener
    list[str]
        List of stocks
    bool
        Whether some random stock selection due to limitations
