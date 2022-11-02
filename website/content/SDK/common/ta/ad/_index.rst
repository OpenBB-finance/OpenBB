.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Calculate AD technical indicator
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
common.ta.ad(
    data: pandas.core.frame.DataFrame,
    use_open: bool = False,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    data : *pd.DataFrame*
        Dataframe of prices with OHLC and Volume
    use_open : *bool*
        Whether to use open prices
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        Dataframe with technical indicator
