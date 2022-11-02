.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get number of companies per country in a specific industry (and specific market cap).
    [Source: Finance Database]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.sia.cpci(
    industry: str = 'Internet Content & Information', mktcap: str = 'Large',
    exclude_exchanges: bool = True,
    chart: bool = False,
) -> dict
{{< /highlight >}}

* **Parameters**

    industry: *str*
        Select industry to get number of companies by each country
    mktcap: *str*
        Select market cap of companies to consider from Small, Mid and Large
    exclude_exchanges : *bool*
        Exclude international exchanges

    
* **Returns**

    dict
        Dictionary of countries and number of companies in a specific sector
   