.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get info about tokens on you ethereum blockchain balance. Eth balance, balance of all tokens which
    have name and symbol. [Source: Ethplorer]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.onchain.balance(
    address: str,
    sortby: str = 'index',
    ascend: bool = False,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    address: *str*
        Blockchain balance e.g. 0x3cD751E6b0078Be393132286c442345e5DC49699
    sortby: *str*
        Key to sort by.
    ascend: *str*
        Sort in descending order.
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame:
        DataFrame with list of tokens and their balances.
