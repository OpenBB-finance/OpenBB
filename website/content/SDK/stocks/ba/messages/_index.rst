.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get last messages for a given ticker [Source: stocktwits]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.ba.messages(
    symbol: str,
    limit: int = 30,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Stock ticker symbol
    limit : *int*
        Number of messages to get

    
* **Returns**

    pd.DataFrame
        Dataframe of messages
   