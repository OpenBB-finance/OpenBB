.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get list of tokens trade-able on Uniswap DEX. [Source: https://thegraph.com/en/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.defi.tokens(
    skip: int = 0,
    limit: int = 100,
    sortby: str = 'index',
    ascend: bool = False,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    skip: *int*
        Skip n number of records.
    limit: *int*
        Show n number of records.
    sortby: *str*
        The column to sort by
    ascend: *bool*
        Whether to sort in ascending order
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        Uniswap tokens with trading volume, transaction count, liquidity.
