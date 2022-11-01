.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns coin tokenomics
    [Source: https://messari.io/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.dd.tk(
    symbol: str,
    coingecko_id: str,
    chart: bool = False
) -> Tuple[pandas.core.frame.DataFrame, pandas.core.frame.DataFrame]
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Crypto symbol to check tokenomics
    coingecko_id : *str*
        ID from coingecko
    
* **Returns**

    pd.DataFrame
        Metric Value tokenomics
    pd.DataFrame
        Circulating supply overtime
    