.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get hour-level sentiment data for the chosen symbol

    Source: [Sentiment Investor]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
stocks.ba.hist(
    symbol: str,
    start_date: str = '2022-10-26',
    end_date: str = '2022-11-02',
    number: int = 100,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Ticker to view sentiment data
    start_date: *str*
        Initial date like string or unix timestamp (e.g. 12-21-2021)
    end_date: *str*
        End date like string or unix timestamp (e.g. 12-21-2021)
    number : *int*
        Number of results returned by API call
        Maximum 250 per api call
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        Dataframe of historical sentiment
