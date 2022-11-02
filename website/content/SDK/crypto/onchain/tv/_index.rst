.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get token volume on different Decentralized Exchanges. [Source: https://graphql.bitquery.io/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.onchain.tv(
    symbol: str = 'UNI',
    trade_amount_currency: str = 'USD',
    sortby: str = 'tradeAmount',
    ascend: bool = True,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        ERC20 token symbol.
    trade_amount_currency: *str*
        Currency to display trade amount in.
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
        Token volume on Decentralized Exchanges
