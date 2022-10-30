.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Center of gravity
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
common.ta.cg(values: pandas.core.series.Series, window: int, chart = False) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    values: *pd.DataFrame*
        Data to use with close being titled values
    window: *int*
        Length for indicator window
    
* **Returns**

    pd.DataFrame
        Dataframe of technical indicator
    