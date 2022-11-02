.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get historical yield for a given maturity
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
economy.tyld(
    interval: str = 'm',
    maturity: str = '10y',
    start_date: str = '2010-01-01',
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    interval : *str*
        Interval for data.  Can be "d","w","m" for daily, weekly or monthly, by default "m"
    start_date: *str*
        Start date for data.  Should be in YYYY-MM-DD format, by default "2010-01-01"
    maturity : *str*
        Maturity timeline.  Can be "3mo","5y","10y" or "30y", by default "10y"
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        Dataframe of historical yields
