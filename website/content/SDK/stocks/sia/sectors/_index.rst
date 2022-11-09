.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.sia.sectors(
    industry: str = '',
    country: str = '',
    chart: bool = False,
) -> list
{{< /highlight >}}

.. raw:: html

    <p>
    Get all sectors in Yahoo Finance data based on country or industry. [Source: Finance Database]
    </p>

* **Parameters**

    industry : str
        Filter retrieved sectors by industry
    country : str
        Filter retrieved sectors by country

* **Returns**

    list
        List of possible sectors
