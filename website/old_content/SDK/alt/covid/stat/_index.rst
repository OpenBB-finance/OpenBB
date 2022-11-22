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
alt.covid.stat(
    country, stat: str = 'cases',
    limit: int = 10,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Show historical cases and deaths by country
    </p>

* **Parameters**

    country: str
        Country to get data for
    stat: str
        Statistic to get.  Either "cases", "deaths" or "rates"
    limit: int
        Number of raw data to show
    chart: bool
       Flag to display chart


|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
alt.covid.stat(
    country, stat: str = 'cases',
    raw: bool = False,
    limit: int = 10,
    export: str = '',
    plot: bool = True,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Show historical cases and deaths by country
    </p>

* **Parameters**

    country: str
        Country to get data for
    stat: str
        Statistic to get.  Either "cases", "deaths" or "rates"
    raw: bool
        Flag to display raw data
    limit: int
        Number of raw data to show
    export: str
        Format to export data
    plot : bool
        Flag to plot data
    chart: bool
       Flag to display chart

