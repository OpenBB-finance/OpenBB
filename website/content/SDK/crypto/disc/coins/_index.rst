.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get N coins from CoinGecko [Source: CoinGecko]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.disc.coins(
    limit: int = 250,
    category: str = '', sortby='Symbol',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    limit: *int*
        Number of top coins to grab from CoinGecko
    sortby: *str*
        Key to sort data

    
* **Returns**

    pandas.DataFrame
        N coins
    