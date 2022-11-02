.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get number of companies per industry in a specific sector (and specific market cap).
    [Source: Finance Database]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
stocks.sia.cpis(
    sector: str = 'Technology',
    mktcap: str = 'Large',
    exclude_exchanges: bool = True,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> dict
{{< /highlight >}}

* **Parameters**

    sector: *str*
        Select sector to get number of companies by each industry
    mktcap: *str*
        Select market cap of companies to consider from Small, Mid and Large
    exclude_exchanges : *bool*
        Exclude international exchanges
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    dict
        Dictionary of industries and number of companies in a specific sector
