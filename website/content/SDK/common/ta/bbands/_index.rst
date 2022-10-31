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
    close_values: pandas.core.series.Series,
    window: int = 15,
    n_std: float = 2,
    mamode: str = 'ema',
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    close_values : *pd.DataFrame*
        DataFrame of sclose prices
    window : *int*
        Length of window to calculate BB
    n_std : *float*
        Number of standard deviations to show
    mamode : *str*
        Method of calculating average

    
* **Returns**

    df_ta: *pd.DataFrame*
        Dataframe of bollinger band data
    