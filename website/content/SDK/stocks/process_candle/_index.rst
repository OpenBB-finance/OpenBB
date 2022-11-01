.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Process DataFrame into candle style plot
    </h3>

{{< highlight python >}}
stocks.process_candle(
    data: pandas.core.frame.DataFrame,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    data : *DataFrame*
        Stock dataframe.

    
* **Returns**

    DataFrame
        A Panda's data frame with columns Open, High, Low, Close, Adj Close, Volume,
        date_id, OC-High, OC-Low.
    