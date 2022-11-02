.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get last N trades for chosen trading pair. [Source: Coinbase]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.dd.trades(
    symbol: str,
    limit: int = 1000,
    side: Optional[Any] = None,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH
    limit: *int*
        Last <limit> of trades. Maximum is 1000.
    side: *str*
        You can chose either sell or buy side. If side is not set then all trades will be displayed.
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        Last N trades for chosen trading pairs.
