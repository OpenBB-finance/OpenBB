.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get the omega series
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
common.qa.omega(
    data: pandas.core.frame.DataFrame,
    threshold\_start: float = 0,
    threshold\_end: float = 1.5,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    data: *pd.DataFrame*
        stock dataframe
    threshold\_start: *float*
        annualized target return threshold start of plotted threshold range
    threshold\_end: *float*
        annualized target return threshold end of plotted threshold range
    