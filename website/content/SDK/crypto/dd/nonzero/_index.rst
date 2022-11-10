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
crypto.dd.nonzero(
    symbol: str,
    start_date: int = 1262322000,
    end_date: int = 1668033690,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Returns addresses with non-zero balance of a certain symbol
    [Source: https://glassnode.com]
    </p>

* **Parameters**

    symbol : str
        Asset to search (e.g., BTC)
    start_date : int
        Initial date timestamp (e.g., 1_577_836_800)
    end_date : int
        End date timestamp (e.g., 1_609_459_200)
    chart: *bool*
       Flag to display chart


* **Returns**

    pd.DataFrame
        addresses with non-zero balances

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.dd.nonzero(
    symbol: str,
    start_date: int = 1577836800,
    end_date: int = 1609459200,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display addresses with non-zero balance of a certain symbol
    [Source: https://glassnode.org]
    </p>

* **Parameters**

    symbol : str
        Asset to search (e.g., BTC)
    start_date : int
        Initial date timestamp (e.g., 1_577_836_800)
    end_date : int
        End date timestamp (e.g., 1_609_459_200)
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: *bool*
       Flag to display chart

