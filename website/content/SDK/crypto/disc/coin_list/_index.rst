.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get list of coins available on CoinGecko [Source: CoinGecko]

    Returns
    -------
    pandas.DataFrame
        Coins available on CoinGecko
        Columns: id, symbol, name
    </h3>

{{< highlight python >}}
crypto.disc.coin_list(
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Returns**

    pandas.DataFrame
        Coins available on CoinGecko
        Columns: id, symbol, name
    