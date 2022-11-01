.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns coin roadmap
    [Source: https://messari.io/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.dd.rm(
    symbol: str,
    ascend: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Crypto symbol to check roadmap
    ascend: *bool*
        reverse order

    
* **Returns**

    pd.DataFrame
        roadmap
    