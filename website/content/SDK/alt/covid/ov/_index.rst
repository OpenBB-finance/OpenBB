.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get historical cases and deaths by country
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
alt.covid.ov(
    country, limit: int = 100,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    country: *str*
        Country to get data for
    limit: *int*
        Number of raw data to show
    