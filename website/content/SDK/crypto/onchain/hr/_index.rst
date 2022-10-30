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
    start_date: int = 1288730857,
    end_date: int = 1667162857,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Blockchain to check hashrate (BTC or ETH)
    start_date : *int*
        Initial date timestamp (e.g., 1_614_556_800)
    end_date : *int*
        End date timestamp (e.g., 1_614_556_800)
    interval : *str*
        Interval frequency (e.g., 24h)

    
* **Returns**

    pd.DataFrame
        mean hashrate and symbol price over time
    