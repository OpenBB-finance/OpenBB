.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get all countries in Yahoo Finance data based on sector or industry. [Source: Finance Database]
    </h3>

{{< highlight python >}}
stocks.sia.countries(
    industry: str = '',
    sector: str = '',
) -> list
{{< /highlight >}}

* **Parameters**

    industry : *str*
        Filter retrieved countries by industry
    sector : *str*
        Filter retrieved countries by sector

* **Returns**

    list
        List of possible countries
