.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Gets volume weighted average price (VWAP)
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
common.ta.vwap(
    data: pandas.core.frame.DataFrame,
    offset: int = 0,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    data: *pd.DataFrame*
        Dataframe of dates and prices
    offset: *int*
        Length of offset
    
* **Returns**

    df_vwap: *pd.DataFrame*
        Dataframe with VWAP data
   