.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get trades on Decentralized Exchanges aggregated by DEX [Source: https://graphql.bitquery.io/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.onchain.lt(
    trade_amount_currency: str = 'USD',
    limit: int = 90,
    sortby: str = 'tradeAmount',
    ascend: bool = True,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    trade_amount_currency: *str*
        Currency of displayed trade amount. Default: *USD*
    limit: * int*
        Last n days to query data. Maximum 365 (bigger numbers can cause timeouts
        on server side)
    sortby: *str*
        Key by which to sort data
    ascend: *bool*
        Flag to sort data ascending
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        Trades on Decentralized Exchanges aggregated by DEX
