.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Gets hull moving average (HMA) for stock
    </h3>

{{< highlight python >}}
common.ta.hma(data: pandas.core.frame.DataFrame, length: int = 50, offset: int = 0) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    data: *pd.DataFrame*
        Dataframe of dates and prices
    length: *int*
        Length of SMA window
    offset: *int*
        Length of offset

    
* **Returns**

    df_ta: *pd.DataFrame*
        Dataframe containing prices and HMA
    