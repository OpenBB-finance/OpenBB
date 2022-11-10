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
stocks.gov.lastcontracts(
    past_transaction_days: int = 2,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get last government contracts [Source: quiverquant.com]
    </p>

* **Parameters**

    past_transaction_days: int
        Number of days to look back
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        DataFrame of government contracts

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.gov.lastcontracts(
    past_transaction_days: int = 2,
    limit: int = 20,
    sum_contracts: bool = False,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Last government contracts [Source: quiverquant.com]
    </p>

* **Parameters**

    past_transaction_days: int
        Number of days to look back
    limit: int
        Number of contracts to show
    sum_contracts: bool
        Flag to show total amount of contracts given out.
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

