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
stocks.ba.hist(
    symbol: str,
    start_date: str = None,
    end_date: str = None,
    number: int = 100,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get hour-level sentiment data for the chosen symbol

    Source: [Sentiment Investor]
    </p>

* **Parameters**

    symbol: str
        Ticker to view sentiment data
    start_date: str
        Initial date like string or unix timestamp (e.g. 12-21-2021)
    end_date: str
        End date like string or unix timestamp (e.g. 12-21-2021)
    number : int
        Number of results returned by API call
        Maximum 250 per api call
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Dataframe of historical sentiment

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.ba.hist(
    symbol: str,
    start_date: str = None,
    end_date: str = None,
    number: int = 100,
    raw: bool = False,
    limit: int = 10,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display historical sentiment data of a ticker,
    and plot a chart with RHI and AHI.
    </p>

* **Parameters**

    symbol: str
        Ticker symbol to view sentiment data
    start_date: str
        Initial date like string or unix timestamp (e.g. 2021-12-21)
    end_date: str
        End date like string or unix timestamp (e.g. 2022-01-15)
    number: int
        Number of results returned by API call
        Maximum 250 per api call
    raw: boolean
        Whether to display raw data, by default False
    limit: int
        Number of results display on the terminal
        Default: 10
    export: str
        Format to export data
    external_axes: Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    chart: bool
       Flag to display chart


* **Returns**

    
