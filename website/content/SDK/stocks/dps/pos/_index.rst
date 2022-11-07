.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.dps.pos(
    sortby: str = 'dpp_dollar',
    ascend: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get dark pool short positions. [Source: Stockgrid]
    </p>

* **Parameters**

    sortby : str
        Field for which to sort by, where 'sv': Short Vol. [1M],
        'sv_pct': Short Vol. %%, 'nsv': Net Short Vol. [1M],
        'nsv_dollar': Net Short Vol. ($100M), 'dpp': DP Position [1M],
        'dpp_dollar': DP Position ($1B)
    ascend : bool
        Data in ascending order

* **Returns**

    pd.DataFrame
        Dark pool short position data
