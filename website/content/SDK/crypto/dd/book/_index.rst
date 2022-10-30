.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get order book for currency. [Source: Binance]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.dd.book(
    from\_symbol: str,
    limit: int = 100,
    to\_symbol: str = 'USDT',
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**


    from\_symbol: *str*
        Cryptocurrency symbol
    limit: *int*
        Limit parameter. Adjusts the weight
    to\_symbol: *str*
        Quote currency (what to view coin vs)

    
* **Returns**


    pd.DataFrame
        Dataframe containing orderbook
    