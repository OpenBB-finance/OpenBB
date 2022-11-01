.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get major crypto-related hacks
    [Source: https://rekt.news]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.ov.crypto_hacks(
    sortby: str = 'Platform',
    ascend: bool = False,
    chart: bool = False
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    sortby: *str*
        Key by which to sort data {Platform,Date,Amount [$],Audit,Slug,URL}
    ascend
        Flag to sort data ascending

    
* **Returns**

    pandas.DataFrame:
        Hacks with columns {Platform,Date,Amount [$],Audited,Slug,URL}
    