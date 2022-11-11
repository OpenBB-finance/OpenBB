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
crypto.defi.anchor_data(
    address: str = '',
    chart: bool = False,
) -> Tuple[Any, Any, str]
{{< /highlight >}}

.. raw:: html

    <p>
    Returns anchor protocol earnings data of a certain terra address
    [Source: https://cryptosaurio.com/]
    </p>

* **Parameters**

    address : str
        Terra address. Valid terra addresses start with 'terra'
    chart: bool
       Flag to display chart


* **Returns**

    Tuple:
        - pandas.DataFrame: Earnings over time in UST
        - pandas.DataFrame: History of transactions
        - str:              Overall statistics

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.defi.anchor_data(
    address: str = '',
    export: str = '',
    show_transactions: bool = False,
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Displays anchor protocol earnings data of a certain terra address
    [Source: https://cryptosaurio.com/]
    </p>

* **Parameters**

    asset : str
        Terra asset {ust,luna,sdt}
    address : str
        Terra address. Valid terra addresses start with 'terra'
    show_transactions : bool
        Flag to show history of transactions in Anchor protocol for address. Default False
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

