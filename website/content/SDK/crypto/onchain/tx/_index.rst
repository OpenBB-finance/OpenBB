.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get info about transaction. [Source: Ethplorer]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.onchain.tx(
    tx_hash, chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    tx_hash: *str*
        Transaction hash e.g. 0x9dc7b43ad4288c624fdd236b2ecb9f2b81c93e706b2ffd1d19b112c1df7849e6
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame:
        DataFrame with information about ERC20 token transaction.
