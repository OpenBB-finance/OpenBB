.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get number of companies per sector in a specific country (and specific market cap). [Source: Finance Database]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.sia.cps(
    country: str = 'United States',
    mktcap: str = 'Large',
    exclude\_exchanges: bool = True,
    chart: bool = False,
    ) -> dict
{{< /highlight >}}

* **Parameters**

    country: *str*
        Select country to get number of companies by each sector
    mktcap: *str*
        Select market cap of companies to consider from Small, Mid and Large
    exclude\_exchanges : *bool*
        Exclude international exchanges

    
* **Returns**

    dict
        Dictionary of sectors and number of companies in a specific country
    