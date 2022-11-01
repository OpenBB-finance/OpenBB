.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Gets Sentiment analysis provided by FinBrain's API [Source: finbrain]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.ba.headlines(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Ticker symbol to get the sentiment analysis from

    
* **Returns**

    DataFrame()
        Empty if there was an issue with data retrieval
    