.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns coin product info
    [Source: https://messari.io/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.dd.pi(
    symbol: str,
    chart: bool = False,
    ) -> Tuple[pandas.core.frame.DataFrame, pandas.core.frame.DataFrame, pandas.core.frame.DataFrame, pandas.core.frame.DataFrame]
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Crypto symbol to check product info

    
* **Returns**

    pd.DataFrame
        Metric, Value with project and technology details
    pd.DataFrame
        coin public repos
    pd.DataFrame
        coin audits
    pd.DataFrame
        coin known exploits/vulns
    