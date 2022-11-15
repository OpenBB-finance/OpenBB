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
crypto.ov.btcrb(
    start_date: str = '2010-01-01',
    end_date: str = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Get bitcoin price data
    [Price data from source: https://glassnode.com]
    [Inspired by: https://blockchaincenter.net]
    </p>

* **Parameters**

    start_date : str
        Initial date, format YYYY-MM-DD
    end_date : str
        Final date, format YYYY-MM-DD
    chart: bool
       Flag to display chart


|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.ov.btcrb(
    start_date: str = '2010-01-01',
    end_date: str = None,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Displays bitcoin rainbow chart
    [Price data from source: https://glassnode.com]
    [Inspired by: https://blockchaincenter.net]
    </p>

* **Parameters**

    start_date : str
        Initial date, format YYYY-MM-DD
    end_date : str
        Final date, format YYYY-MM-DD
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

