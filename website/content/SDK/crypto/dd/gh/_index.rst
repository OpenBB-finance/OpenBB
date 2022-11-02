.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns  a list of developer activity for a given coin and time interval.

    [Source: https://santiment.net/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.dd.gh(
    symbol: str,
    dev_activity: bool = False,
    interval: str = '1d',
    start_date: str = '2021-11-02T14:18:33Z',
    end_date: str = '2022-11-02T14:18:33Z',
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Crypto symbol to check github activity
    dev_activity: *bool*
        Whether to filter only for development activity
    start_date : *int*
        Initial date like string (e.g., 2021-10-01)
    end_date : *int*
        End date like string (e.g., 2021-10-01)
    interval : *str*
        Interval frequency (e.g., 1d)
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        developer activity over time
