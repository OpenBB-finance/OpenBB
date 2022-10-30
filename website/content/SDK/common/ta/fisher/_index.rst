.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Fisher Transform
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
common.ta.fisher(
    high\_vals: pandas.core.series.Series,
    low\_vals: pandas.core.series.Series,
    window: int = 14,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    high\_vals: *pd.Series*
        High values
    low\_vals: *pd.Series*
        Low values
    window: *int*
        Length for indicator window
    
* **Returns**

    df\_ta: *pd.DataFrame*
        Dataframe of technical indicator
    