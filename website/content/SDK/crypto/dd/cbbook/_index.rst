.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get orders book for chosen trading pair. [Source: Coinbase]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.dd.cbbook(
    symbol: str,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> Tuple[numpy.ndarray, numpy.ndarray, str, dict]
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    Tuple[np.array, np.array, str, dict]
        array with bid prices, order sizes and cumulative order sizes
        array with ask prices, order sizes and cumulative order sizes
        trading pair
        dict with raw data
