.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > ADX technical indicator
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
common.ta.adx(
    high_values: pandas.core.series.Series,
    low_values: pandas.core.series.Series,
    close_values: pandas.core.series.Series,
    window: int = 14,
    scalar: int = 100,
    drift: int = 1,
    chart: bool = False
)
{{< /highlight >}}

* **Parameters**

    high_values: *pd.Series*
        High prices
    low_values: *pd.Series*
        Low prices
    close_values: *pd.Series*
        close prices
    window: *int*
        Length of window
    scalar: *int*
        Scalar variable
    drift: *int*
        Drift variable

    
* **Returns**

    pd.DataFrame
        DataFrame with adx indicator
    