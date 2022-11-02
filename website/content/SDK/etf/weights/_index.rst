.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Return sector weightings allocation of ETF. [Source: Yahoo Finance]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
etf.weights(
    name: str,
    chart: bool = False,
) -> Dict
{{< /highlight >}}

* **Parameters**

    name: *str*
        ETF name

    
* **Returns**

    Dict
        Dictionary with sector weightings allocation
   