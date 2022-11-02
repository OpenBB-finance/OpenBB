.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get list of crypto indexes from CoinGecko API [Source: CoinGecko]

    Returns
    -------
    pandas.DataFrame
        Name, Id, Market, Last, MultiAsset
    sortby: *str*
        Key by which to sort data
    ascend: *bool*
        Flag to sort data descending
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.ov.cgindexes(
    sortby: str = 'Name',
    ascend: bool = True,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Returns**

    pandas.DataFrame
        Name, Id, Market, Last, MultiAsset
    sortby: *str*
        Key by which to sort data
    ascend: *bool*
        Flag to sort data descending
