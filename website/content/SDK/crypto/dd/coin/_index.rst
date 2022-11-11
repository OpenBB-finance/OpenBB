.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
crypto.dd.coin(
    symbol: str = 'eth-ethereum',
    chart: bool = False,
) -> dict
{{< /highlight >}}

.. raw:: html

    <p>
    Get coin by id [Source: CoinPaprika]
    </p>

* **Parameters**

    symbol: str
        id of coin from coinpaprika e.g. Ethereum - > 'eth-ethereum'

* **Returns**

    dict
        Coin response
