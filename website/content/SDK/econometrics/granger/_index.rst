.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Calculate granger tests
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
econometrics.granger(
    dependent_series, independent_series, lags, chart: bool = False,
)
{{< /highlight >}}

* **Parameters**

    dependent_series: *Series*
        The series you want to test Granger Causality for.
    independent_series: *Series*
        The series that you want to test whether it Granger-causes time_series_y
    lags : *int*
        The amount of lags for the Granger test. By default, this is set to 3.
    