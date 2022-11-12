.. role:: python(code)
    :language: python
    :class: highlight

|

To obtain charts, make sure to add :python:`chart = True` as the last parameter.

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
crypto.onchain.hr(
    symbol: str,
    interval: str = '24h',
    start_date: int = 1289856912,
    end_date: int = 1668288912,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Returns dataframe with mean hashrate of btc or eth blockchain and symbol price
    [Source: https://glassnode.com]
    </p>

* **Parameters**

    symbol : str
        Blockchain to check hashrate (BTC or ETH)
    start_date : int
        Initial date timestamp (e.g., 1_614_556_800)
    end_date : int
        End date timestamp (e.g., 1_614_556_800)
    interval : str
        Interval frequency (e.g., 24h)
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        mean hashrate and symbol price over time

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.onchain.hr(
    symbol: str,
    start_date: int = 1636752912,
    end_date: int = 1668288912,
    interval: str = '24h',
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display dataframe with mean hashrate of btc or eth blockchain and symbol price.
    [Source: https://glassnode.org]
    </p>

* **Parameters**

    symbol : str
        Blockchain to check mean hashrate (BTC or ETH)
    start_date : int
        Initial date timestamp (e.g., 1_614_556_800)
    end_date : int
        End date timestamp (e.g., 1_614_556_800)
    interval : str
        Interval frequency (possible values are: 24, 1w, 1month)
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    chart: bool
       Flag to display chart

