.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get number of unique ethereum addresses which made a transaction in given time interval.
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.onchain.ueat(
    interval: str = 'day',
    limit: int = 90,
    sortby: str = 'tradeAmount',
    ascend: bool = True,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    interval: *str*
        Time interval in which count unique ethereum addresses which made transaction. day,
        month or week.
    limit: *int*
        Number of records for data query.
    sortby: *str*
        Key by which to sort data
    ascend: *bool*
        Flag to sort data ascending
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        Unique ethereum addresses which made a transaction
