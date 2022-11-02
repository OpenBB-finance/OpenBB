.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get top 50 tokens. [Source: Ethplorer]

    Returns
    -------
    pd.DataFrame:
        DataFrame with list of top 50 tokens.
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.onchain.top(
    sortby: str = 'rank',
    ascend: bool = False,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Returns**

    pd.DataFrame:
        DataFrame with list of top 50 tokens.
