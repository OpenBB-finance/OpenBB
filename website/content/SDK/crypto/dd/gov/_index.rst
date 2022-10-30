.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns coin governance
    [Source: https://messari.io/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.dd.gov(
    symbol: str,
    chart: bool = False,
    ) -> Tuple[str, pandas.core.frame.DataFrame]
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Crypto symbol to check governance

    
* **Returns**

    str
        governance summary
    pd.DataFrame
        Metric Value with governance details
    