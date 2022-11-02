.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Compare regression results between Panel Data regressions.
    </h3>

{{< highlight python >}}
econometrics.comparison(
    regressions, export: str = '',
)
{{< /highlight >}}

* **Parameters**

    regressions : *Dict*
        Dictionary with regression results.
    export : *str*
        Format to export data

    
* **Returns**

    Returns a PanelModelComparison which shows an overview of the different regression results.
   