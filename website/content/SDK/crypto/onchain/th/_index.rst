.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get info about token historical transactions. [Source: Ethplorer]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.onchain.th(
    address, sortby: str = 'timestamp',
    ascend: bool = False,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    address: *str*
        Token e.g. 0xf3db5fa2c66b7af3eb0c0b782510816cbe4813b8
    sortby: *str*
        Key to sort by.
    ascend: *str*
        Sort in descending order.
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame:
        DataFrame with token historical transactions.
