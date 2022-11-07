.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
crypto.dd.trading_pair_info(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get information about chosen trading pair. [Source: Coinbase]
    </p>

* **Parameters**

    symbol: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH

* **Returns**

    pd.DataFrame
        Basic information about given trading pair
