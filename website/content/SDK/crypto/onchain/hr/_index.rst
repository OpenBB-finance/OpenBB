.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns dataframe with mean hashrate of btc or eth blockchain and symbol price
    [Source: https://glassnode.com]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.onchain.hr(
    symbol: str,
    interval: str = '24h',
    start\_date: int = 1288740037,
    end\_date: int = 1667172037,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Blockchain to check hashrate (BTC or ETH)
    start\_date : *int*
        Initial date timestamp (e.g., 1\_614\_556\_800)
    end\_date : *int*
        End date timestamp (e.g., 1\_614\_556\_800)
    interval : *str*
        Interval frequency (e.g., 24h)

    
* **Returns**

    pd.DataFrame
        mean hashrate and symbol price over time
    