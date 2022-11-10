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
alt.covid.ov(
    country, limit: int = 100,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get historical cases and deaths by country
    </p>

* **Parameters**

    country: str
        Country to get data for
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
alt.covid.ov(
    country, raw: bool = False,
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
    raw: bool
        Flag to display raw data
    limit: int
        Number of raw data to show
    export: str
        Format to export data
    plot: bool
        Flag to display historical plot
    chart: bool
       Flag to display chart

