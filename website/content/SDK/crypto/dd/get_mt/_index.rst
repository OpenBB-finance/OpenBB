.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns available messari timeseries
    [Source: https://messari.io/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.dd.get_mt(
    only_free: bool = True,
    chart: bool = False
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    only_free : *bool*
        Display only timeseries available for free

    
* **Returns**

    pd.DataFrame
        available timeseries
    