.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Calculate Donchian Channels
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
common.ta.donchian(
    high_prices: pandas.core.series.Series,
    low_prices: pandas.core.series.Series,
    upper_length: int = 20,
    lower_length: int = 20,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    high_prices : *pd.DataFrame*
        High prices
    low_prices : *pd.DataFrame*
        Low prices
    upper_length : *int*
        Length of window to calculate upper channel
    lower_length : *int*
        Length of window to calculate lower channel
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        Dataframe of upper and lower channels
