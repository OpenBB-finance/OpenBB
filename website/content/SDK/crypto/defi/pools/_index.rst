.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get uniswap pools by volume. [Source: https://thegraph.com/en/]

    Returns
    -------
    pd.DataFrame
        Trade-able pairs listed on Uniswap by top volume.
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.defi.pools(
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Returns**

    pd.DataFrame
        Trade-able pairs listed on Uniswap by top volume.
    