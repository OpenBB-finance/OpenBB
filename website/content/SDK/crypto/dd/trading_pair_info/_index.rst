.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get information about chosen trading pair. [Source: Coinbase]
    </h3>

{{< highlight python >}}
crypto.dd.trading_pair_info(
    symbol: str,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH

    
* **Returns**

    pd.DataFrame
        Basic information about given trading pair
   