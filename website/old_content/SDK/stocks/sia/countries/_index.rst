.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.sia.countries(
    industry: str = '',
    sector: str = '',
    chart: bool = False,
) -> list
{{< /highlight >}}

.. raw:: html

    <p>
    Get all countries in Yahoo Finance data based on sector or industry. [Source: Finance Database]
    </p>

* **Parameters**

    industry : str
        Filter retrieved countries by industry
    sector : str
        Filter retrieved countries by sector

* **Returns**

    list
        List of possible countries
