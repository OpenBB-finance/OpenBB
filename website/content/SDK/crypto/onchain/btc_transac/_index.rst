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
crypto.onchain.btc_transac() -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Returns BTC confirmed transactions [Source: https://api.blockchain.info/]
    </p>

* **Returns**

    pd.DataFrame
        BTC confirmed transactions

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.onchain.btc_transac(
    start_date: int = 1262304000,
    end_date: int = 1667785405,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Returns BTC confirmed transactions [Source: https://api.blockchain.info/]
    </p>

* **Parameters**

    since : *int*
        Initial date timestamp (e.g., 1_609_459_200)
    until : *int*
        End date timestamp (e.g., 1_641_588_030)
    export : *str*
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: *bool*
       Flag to display chart

