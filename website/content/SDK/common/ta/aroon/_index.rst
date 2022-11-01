.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Aroon technical indicator
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
common.ta.aroon(
    high_values: pandas.core.series.Series,
    low_values: pandas.core.series.Series,
    window: int = 25,
    scalar: int = 100,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    high_values: *pd.Series*
        High prices
    low_values: *pd.Series*
        Low prices
    window : *int*
        Length of window
    scalar : *int*
        Scalar variable

    
* **Returns**

    pd.DataFrame
        DataFrame with aroon indicator
    