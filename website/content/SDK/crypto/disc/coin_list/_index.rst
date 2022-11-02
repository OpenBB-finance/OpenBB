.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
crypto.disc.coin_list() -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get list of coins available on CoinGecko [Source: CoinGecko]
    </p>

* **Returns**

    pandas.DataFrame
        Coins available on CoinGecko
        Columns: id, symbol, name
