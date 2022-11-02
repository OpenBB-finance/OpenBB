.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Display top dApps (in terms of TVL) grouped by chain.
    [Source: https://docs.llama.fi/api]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.defi.gdapps(
    limit: int = 50,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    limit: *int*
        Number of top dApps to display
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        Information about DeFi protocols grouped by chain
