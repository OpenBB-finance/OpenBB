.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get the last 100 swaps done on Uniswap [Source: https://thegraph.com/en/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.defi.swaps(
    limit: int = 100,
    sortby: str = 'timestamp',
    ascend: bool = False,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    limit: *int*
        Number of swaps to return. Maximum possible number: *1000.*
    sortby: *str*
        Key by which to sort data. The table can be sorted by every of its columns
        (see https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2).
    ascend: *bool*
        Flag to sort data descending
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        Last 100 swaps on Uniswap
