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
crypto.defi.luna_supply(
    supply_type: str = 'lunaSupplyChallengeStats',
    days: int = 30,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get supply history of the Terra ecosystem

    Source: [Smartstake.io]
    </p>

* **Parameters**

    supply_type: str
        Supply type to unpack json
    days: int
        Day count to fetch data
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Dataframe of supply history data

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.defi.luna_supply(
    days: int = 30,
    export: str = '',
    supply_type: str = 'lunaSupplyChallengeStats',
    limit: int = 5,
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display Luna circulating supply stats
    </p>

* **Parameters**

    days: int
        Number of days
    supply_type: str
        Supply type to unpack json
    export: str
        Export type
    limit: int
        Number of results display on the terminal
        Default: 5
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

