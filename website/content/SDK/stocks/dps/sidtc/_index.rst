.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get short interest and days to cover. [Source: Stockgrid]
    </h3>

{{< highlight python >}}
stocks.dps.sidtc(
    sortby: str = 'float',
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    sortby : *str*
        Field for which to sort by, where 'float': Float Short %%,
        'dtc': Days to Cover, 'si': *Short Interest*

* **Returns**

    pd.DataFrame
        Short interest and days to cover data
