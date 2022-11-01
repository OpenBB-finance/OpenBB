.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Return summary description of ETF. [Source: Yahoo Finance]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
etf.summary(
    name: str,
    chart: bool = False
) -> str
{{< /highlight >}}

* **Parameters**

    name: *str*
        ETF name

    
* **Returns**

    str
        Summary description of the ETF
    