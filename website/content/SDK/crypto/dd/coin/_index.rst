.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get coin by id [Source: CoinPaprika]
    </h3>

{{< highlight python >}}
crypto.dd.coin(
    symbol: str = 'eth-ethereum',
) -> dict
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        id of coin from coinpaprika e.g. Ethereum - > 'eth-ethereum'
    
* **Returns**

    dict
        Coin response
    