.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.dd.arktrades(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Gets a dataframe of ARK trades for ticker
    </p>

* **Parameters**

    symbol : str
        Ticker to get trades for

* **Returns**

    pd.DataFrame
        DataFrame of trades
