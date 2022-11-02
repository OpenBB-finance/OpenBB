.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Stochastic oscillator
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
common.ta.stoch(
    high_vals: pandas.core.series.Series,
    low_vals: pandas.core.series.Series,
    close_vals: pandas.core.series.Series,
    fastkperiod: int = 14,
    slowdperiod: int = 3,
    slowkperiod: int = 3,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
)
{{< /highlight >}}

* **Parameters**

    high_vals: *pd.Series*
        High values
    low_vals: *pd.Series*
        Low values
    close-vals: *pd.Series*
        Close values
    fastkperiod : *int*
        Fast k period
    slowdperiod : *int*
        Slow d period
    slowkperiod : *int*
        Slow k period
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        Dataframe of technical indicator
