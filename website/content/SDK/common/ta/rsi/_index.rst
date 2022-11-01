.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Relative strength index
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
common.ta.rsi(
    values: pandas.core.series.Series,
    window: int = 14,
    scalar: float = 100,
    drift: int = 1,
    chart: bool = False
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    values: *pd.Series*
        Dataframe of prices
    window: *int*
        Length of window
    scalar: *float*
        Scalar variable
    drift: *int*
        Drift variable

    
* **Returns**

    pd.DataFrame
        Dataframe of technical indicator
    