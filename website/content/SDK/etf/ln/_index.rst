.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Return a selection of ETFs based on name filtered by total assets. [Source: Finance Database]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
etf.ln(
    name: str,
    chart: bool = False
) -> Dict
{{< /highlight >}}

* **Parameters**

    name: *str*
        Search by name to find ETFs matching the criteria.

    
* **Returns**

    data : *Dict*
        Dictionary with ETFs that match a certain name
    