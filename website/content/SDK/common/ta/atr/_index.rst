.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Average True Range
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
common.ta.atr(
    high\_prices: pandas.core.series.Series,
    low\_prices: pandas.core.series.Series,
    close\_prices: pandas.core.series.Series,
    window: int = 14,
    mamode: str = 'ema',
    offset: int = 0,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    high_prices : *pd.DataFrame*
        High prices
    low_prices : *pd.DataFrame*
        Low prices
    close_prices : *pd.DataFrame*
        Close prices
    window : *int*
        Length of window
    mamode: *str*
        Type of filter
    offset : *int*
        Offset value

    
* **Returns**

    pd.DataFrame
        Dataframe of atr
    