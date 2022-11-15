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
economy.spectrum(
    group: str = 'sector',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Get group (sectors, industry or country) valuation/performance data. [Source: Finviz]
    </p>

* **Parameters**

    group : str
       Group by category. Available groups can be accessed through get_groups().
    chart: bool
       Flag to display chart


|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
economy.spectrum(
    group: str = 'sector',
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display finviz spectrum in system viewer [Source: Finviz]
    </p>

* **Parameters**

    group: str
        Group by category. Available groups can be accessed through get_groups().
    export: str
        Format to export data
    chart: bool
       Flag to display chart

