.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Shows top n coins. [Source: CoinMarketCap]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.disc.cmctop(
    sortby: str = 'CMC_Rank',
    ascend: bool = True,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    sortby: *str*
        Key to sort data. The table can be sorted by every of its columns. Refer to
        Coin Market Cap:s API documentation, see:
        https://coinmarketcap.com/api/documentation/v1/#operation/getV1CryptocurrencyListingsLatest
    ascend: *bool*
        Whether to sort ascending or descending
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        Top coin on CoinMarketCap
