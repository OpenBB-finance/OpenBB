.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get group (sectors, industry or country) valuation/performance data. [Source: Finviz]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
economy.spectrum(
    group: str = 'sector',
    chart: bool = False,
    )
{{< /highlight >}}

* **Parameters**

    group : *str*
       Group by category. Available groups can be accessed through get\_groups().
    