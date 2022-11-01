.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get account holdings for asset. [Source: Binance]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.dd.balance(
    from_symbol: str,
    to_symbol: str = 'USDT',
    chart: bool = False
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    from_symbol: *str*
        Cryptocurrency
    to_symbol: *str*
        Cryptocurrency

    
* **Returns**

    pd.DataFrame
        Dataframe with account holdings for an asset
    