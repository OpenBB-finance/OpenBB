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
stocks.ba.trend(
    start_date: datetime.datetime = datetime.datetime(
    2022, 11, 10, 16, 14, 15, 505378, chart: bool = False,
), hour: int = 0,
    number: int = 10,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get sentiment data on the most talked about tickers
    within the last hour

    Source: [Sentiment Investor]
    </p>

* **Parameters**

    start_date: datetime
        Datetime object (e.g. datetime(2021, 12, 21)
    hour: int
        Hour of the day in 24-hour notation (e.g. 14)
    number : int
        Number of results returned by API call
        Maximum 250 per api call
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Dataframe of trending data

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.ba.trend(
    start_date: datetime.datetime = datetime.datetime(
    2022, 11, 10, 16, 14, 15, 505601, chart: bool = False,
), hour: int = 0,
    number: int = 10,
    limit: int = 10,
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display most talked about tickers within
    the last hour together with their sentiment data.
    </p>

* **Parameters**

    start_date: datetime
        Datetime object (e.g. datetime(2021, 12, 21)
    hour: int
        Hour of the day in 24-hour notation (e.g. 14)
    number : int
        Number of results returned by API call
        Maximum 250 per api call
    limit: int
        Number of results display on the terminal
        Default: 10
    export: str
        Format to export data
    chart: bool
       Flag to display chart

