.. role:: python(code)
    :language: python
    :class: highlight

|

To obtain charts, make sure to add :python:`chart = True` as the last parameter.

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.sia.cpcs(
    sector: str = 'Technology',
    mktcap: str = 'Large',
    exclude_exchanges: bool = True,
    chart: bool = False,
) -> dict
{{< /highlight >}}

.. raw:: html

    <p>
    Get number of companies per country in a specific sector (and specific market cap).
    [Source: Finance Database]
    </p>

* **Parameters**

    sector: str
        Select sector to get number of companies by each country
    mktcap: str
        Select market cap of companies to consider from Small, Mid and Large
    exclude_exchanges : bool
        Exclude international exchanges
    chart: bool
       Flag to display chart


* **Returns**

    dict
        Dictionary of countries and number of companies in a specific sector

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.sia.cpcs(
    sector: str = 'Technology',
    mktcap: str = 'Large',
    exclude_exchanges: bool = True,
    export: str = '',
    raw: bool = False,
    max_countries_to_display: int = 15,
    min_pct_to_display_country: float = 0.015,
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display number of companies per country in a specific sector. [Source: Finance Database]
    </p>

* **Parameters**

    sector: str
        Select sector to get number of companies by each country
    mktcap: str
        Select market cap of companies to consider from Small, Mid and Large
    exclude_exchanges : bool
        Exclude international exchanges
    export: str
        Format to export data as
    raw: bool
        Output all raw data
    max_countries_to_display: int
        Maximum number of countries to display
    min_pct_to_display_country: float
        Minimum percentage to display country
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

