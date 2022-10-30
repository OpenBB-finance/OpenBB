.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get sentiment data on the most talked about tickers
    within the last hour

    Source: [Sentiment Investor]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.ba.trend(
    start\_date: datetime.datetime = datetime.datetime(
    2022, 10, 30, 23, 20, 37, 517435, chart: bool = False, ),
    hour: int = 0,
    number: int = 10,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    start\_date: *datetime*
        Datetime object (e.g. datetime(2021, 12, 21)
    hour: *int*
        Hour of the day in 24-hour notation (e.g. 14)
    number : *int*
        Number of results returned by API call
        Maximum 250 per api call

    
* **Returns**

    pd.DataFrame
        Dataframe of trending data
    