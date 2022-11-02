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

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
stocks.ba.trend(
    start_date: datetime.datetime = datetime.datetime(
    2022, 11, 2, 14, 5, 27, 550871, chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
), hour: int = 0,
    number: int = 10,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    start_date: *datetime*
        Datetime object (e.g. datetime(2021, 12, 21)
    hour: *int*
        Hour of the day in 24-hour notation (e.g. 14)
    number : *int*
        Number of results returned by API call
        Maximum 250 per api call
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        Dataframe of trending data
