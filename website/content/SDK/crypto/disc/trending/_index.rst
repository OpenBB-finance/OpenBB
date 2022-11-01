.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns trending coins [Source: CoinGecko]

    Parameters
    ----------
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.disc.trending(
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**


    
* **Returns**

    pandas.DataFrame:
        Trending Coins
    