.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > View historical price of stocks that meet preset
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.screener.historical(
    preset\_loaded: str = 'top\_gainers', limit: int = 10,
    start\_date: str = '2022-05-03', type\_candle: str = 'a',
    normalize: bool = True,
    chart: bool = False,
    )
{{< /highlight >}}

* **Parameters**

    preset\_loaded: *str*
        Preset loaded to filter for tickers
    limit: *int*
        Number of stocks to display
    start\_date: *str*
        Start date to display historical data, in YYYY-MM-DD format
    type\_candle: *str*
        Type of candle to display
    normalize : *bool*
        Boolean to normalize all stock prices using MinMax

    
* **Returns**

    pd.DataFrame
        Dataframe of the screener
    list[str]
        List of stocks
    bool
        Whether some random stock selection due to limitations
    