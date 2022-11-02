.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Gets a dataframe of ARK trades for ticker
    </h3>

{{< highlight python >}}
stocks.dd.arktrades(
    symbol: str,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Ticker to get trades for

* **Returns**

    pd.DataFrame
        DataFrame of trades
