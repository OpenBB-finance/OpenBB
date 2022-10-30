.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Keltner Channels
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
common.ta.kc(
    high_prices: pandas.core.series.Series,
    low_prices: pandas.core.series.Series,
    close_prices: pandas.core.series.Series,
    window: int = 20,
    scalar: float = 2,
    mamode: str = 'ema',
    offset: int = 0,
    chart = False,
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
    scalar: *float*
        Scalar value
    mamode: *str*
        Type of filter
    offset : *int*
        Offset value

    
* **Returns**

    pd.DataFrame
        Dataframe of rolling kc
    