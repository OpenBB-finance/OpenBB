.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get lastly added trade-able pairs on Uniswap with parameters like:
        * number of days the pair has been active,
        * minimum trading volume,
        * minimum liquidity,
        * number of transactions.

    [Source: https://thegraph.com/en/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.defi.pairs(
    last_days: int = 14,
    min_volume: int = 100,
    min_liquidity: int = 0,
    min_tx: int = 100,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    last_days: *int*
        How many days back to look for added pairs.
    min_volume: *int*
        Minimum volume
    min_liquidity: *int*
        Minimum liquidity
    min_tx: *int*
        Minimum number of transactions done in given pool.
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        Lastly added pairs on Uniswap DEX.
