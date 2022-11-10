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
crypto.defi.sreturn(
    limit: int = 200,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Get terra blockchain staking returns history [Source: https://fcd.terra.dev/v1]
    </p>

* **Parameters**

    limit: int
        The number of returns to show
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        historical staking returns

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.defi.sreturn(
    limit: int = 90,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display terra blockchain staking returns history [Source: https://fcd.terra.dev/swagger]
    </p>

* **Parameters**

    limit: int
        Number of records to display
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

