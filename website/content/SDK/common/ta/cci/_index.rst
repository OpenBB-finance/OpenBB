.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Commodity channel index
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
common.ta.cci(
    data: pandas.core.frame.DataFrame,
    window: int = 14,
    scalar: float = 0.0015,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    high_vals: *pd.Series*
        High values
    low_values: *pd.Series*
        Low values
    close-values: *pd.Series*
        Close values
    window: *int*
        Length of window
    scalar: *float*
        Scalar variable

    
* **Returns**

    pd.DataFrame
        Dataframe of technical indicator
    