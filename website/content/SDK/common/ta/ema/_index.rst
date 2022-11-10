.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
common.ta.ema(
    data: pandas.core.series.Series,
    length: int = 50,
    offset: int = 0,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Gets exponential moving average (EMA) for stock
    </p>

* **Parameters**

    data: pd.Series
        Dataframe of dates and prices
    length: int
        Length of EMA window
    offset: int
        Length of offset

* **Returns**

    pd.DataFrame
        Dataframe containing prices and EMA
