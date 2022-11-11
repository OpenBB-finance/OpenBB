.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.process_candle(
    data: pandas.core.frame.DataFrame,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Process DataFrame into candle style plot.
    </p>

* **Parameters**

    data : DataFrame
        Stock dataframe.

* **Returns**

    DataFrame
        A Panda's data frame with columns Open, High, Low, Close, Adj Close, Volume,
        date_id, OC-High, OC-Low.
