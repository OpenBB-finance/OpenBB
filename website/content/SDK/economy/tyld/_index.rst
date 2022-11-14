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
economy.tyld(
    interval: str = 'm',
    maturity: str = '10y',
    start_date: str = '2010-01-01',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get historical yield for a given maturity
    </p>

* **Parameters**

    interval : str
        Interval for data.  Can be "d","w","m" for daily, weekly or monthly, by default "m"
    start_date: str
        Start date for data.  Should be in YYYY-MM-DD format, by default "2010-01-01"
    maturity : str
        Maturity timeline.  Can be "3mo","5y","10y" or "30y", by default "10y"
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Dataframe of historical yields

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
economy.tyld(
    interval: str = 'm',
    maturity: str = '10y',
    start_date: str = '2010-01-01',
    raw: bool = False,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display historical treasury yield for given maturity
    </p>

* **Parameters**

    interval : str
        Interval for data.  Can be "d","w","m" for daily, weekly or monthly, by default "m"
    maturity : str
        Maturity timeline.  Can be "3mo","5y","10y" or "30y", by default "10y"
    start_date: str
        Start date for data.  Should be in YYYY-MM-DD format, by default "2010-01-01"
    raw : bool, optional
        Flag to display raw data, by default False
    export : str, optional
        Format to export data, by default ""
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

