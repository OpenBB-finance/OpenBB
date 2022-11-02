.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Moving average convergence divergence
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
common.ta.macd(
    values: pandas.core.frame.DataFrame,
    n_fast: int = 12,
    n_slow: int = 26,
    n_signal: int = 9,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    values: *pd.Series*
        Values for calculation
    n_fast : *int*
        Fast period
    n_slow : *int*
        Slow period
    n_signal : *int*
        Signal period
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        Dataframe of technical indicator
