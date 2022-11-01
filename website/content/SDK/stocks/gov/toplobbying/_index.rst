.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Corporate lobbying details
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.gov.toplobbying(
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

s

    
* **Returns**

    pd.DataFrame
        DataFrame of top corporate lobbying

    