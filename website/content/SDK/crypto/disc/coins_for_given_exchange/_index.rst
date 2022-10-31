.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Helper method to get all coins available on binance exchange [Source: CoinGecko]
    </h3>

{{< highlight python >}}
crypto.disc.coins_for_given_exchange(
    exchange\_id: str = 'binance',
    page: int = 1,
    ) -> dict
{{< /highlight >}}

* **Parameters**

    exchange_id: *str*
        id of exchange
    page: *int*
        number of page. One page contains 100 records

    
* **Returns**

    dict
        dictionary with all trading pairs on binance
    