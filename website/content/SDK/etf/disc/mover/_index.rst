.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Scrape data for top etf movers.
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
etf.disc.mover(
    sort_type: str = 'gainers',
    export: bool = False,
    chart: bool = False
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    sort_type: *str*
        Data to get.  Can be "gainers", "decliners" or "active"

    
* **Returns**

    etfmovers: *pd.DataFrame*
        Datafame containing the name, price, change and the volume of the etf
    