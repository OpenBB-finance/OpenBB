.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Helper methods that for every coin available on Binance add all quote assets. [Source: Binance]
    </h3>

{{< highlight python >}}
crypto.dd.binance_available_quotes_for_each_coin() -> dict
{{< /highlight >}}

* **Returns**

    dict:
        All quote assets for given coin
        {'ETH' : ['BTC', 'USDT' ...], 'UNI' : ['ETH', 'BTC','BUSD', ...]

   