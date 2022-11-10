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
etf.disc.mover(
    sort_type: str = 'gainers',
    export: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Scrape data for top etf movers.
    </p>

* **Parameters**

    sort_type: str
        Data to get. Can be "gainers", "decliners" or "active"
    chart: bool
       Flag to display chart


* **Returns**

    etfmovers: pd.DataFrame
        Datafame containing the name, price, change and the volume of the etf

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
etf.disc.mover(
    sort_type: str = 'gainers',
    limit: int = 10, export='',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Show top ETF movers from wsj.com
    </p>

* **Parameters**

    sort_type: str
        What to show. Either Gainers, Decliners or Activity
    limit: int
        Number of etfs to show
    export: str
        Format to export data
    chart: bool
       Flag to display chart

