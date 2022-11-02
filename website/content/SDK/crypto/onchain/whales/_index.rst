.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Whale Alert's API allows you to retrieve live and historical transaction data from major blockchains.
    Supported blockchain: Bitcoin, Ethereum, Ripple, NEO, EOS, Stellar and Tron. [Source: https://docs.whale-alert.io/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.onchain.whales(
    min_value: int = 800000,
    limit: int = 100,
    sortby: str = 'date',
    ascend: bool = False,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    min_value: *int*
        Minimum value of trade to track.
    limit: *int*
        Limit of transactions. Max 100
    sortby: *str*
        Key to sort by.
    ascend: *str*
        Sort in ascending order.
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        Crypto wales transactions
