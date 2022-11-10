.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.sia.industries(
    country: str = '',
    sector: str = '',
    chart: bool = False,
) -> list
{{< /highlight >}}

.. raw:: html

    <p>
    Get all industries in Yahoo Finance data based on country or sector. [Source: Finance Database]
    </p>

* **Parameters**

    country : str
        Filter retrieved industries by country
    sector : str
        Filter retrieved industries by sector

* **Returns**

    list
        List of possible industries
