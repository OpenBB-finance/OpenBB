.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get data on selected indices over time [Source: Yahoo Finance]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
economy.index(
    indices: list,
    interval: str = '1d',
    start_date: int = None,
    end_date: int = None,
    column: str = 'Adj Close',
    returns: bool = False,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    indices: *list*
        A list of indices to get data. Available indices can be accessed through economy.available_indices().
    interval: *str*
        Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        Intraday data cannot extend last 60 days
    start_date : *str*
        The starting date, format "YEAR-MONTH-DAY", i.e. 2010-12-31.
    end_date : *str*
        The end date, format "YEAR-MONTH-DAY", i.e. 2020-06-05.
    column : *str*
        Which column to load in, by default this is the Adjusted Close.
    returns: *bool*
        Flag to show cumulative returns on index
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.Dataframe
        Dataframe with historical data on selected indices.
