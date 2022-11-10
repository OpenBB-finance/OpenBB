.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
common.ta.wma(
    data: pandas.core.series.Series,
    length: int = 50,
    offset: int = 0,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Gets weighted moving average (WMA) for stock
    </p>

* **Parameters**

    data: pd.Series
        Dataframe of dates and prices
    length: int
        Length of SMA window
    offset: int
        Length of offset

* **Returns**

    df_ta: pd.DataFrame
        Dataframe containing prices and WMA
