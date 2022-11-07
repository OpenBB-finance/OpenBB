.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
crypto.disc.coins_for_given_exchange(
    exchange_id: str = 'binance',
    page: int = 1,
    chart: bool = False,
) -> dict
{{< /highlight >}}

.. raw:: html

    <p>
    Helper method to get all coins available on binance exchange [Source: CoinGecko]
    </p>

* **Parameters**

    exchange_id: str
        id of exchange
    page: int
        number of page. One page contains 100 records

* **Returns**

    dict
        dictionary with all trading pairs on binance
