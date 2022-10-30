.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Calculate Bollinger Bands
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
common.ta.bbands(
    close\_values: pandas.core.series.Series,
    window: int = 15,
    n\_std: float = 2,
    mamode: str = 'ema',
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    close\_values : *pd.DataFrame*
        DataFrame of sclose prices
    window : *int*
        Length of window to calculate BB
    n\_std : *float*
        Number of standard deviations to show
    mamode : *str*
        Method of calculating average

    
* **Returns**

    df\_ta: *pd.DataFrame*
        Dataframe of bollinger band data
    