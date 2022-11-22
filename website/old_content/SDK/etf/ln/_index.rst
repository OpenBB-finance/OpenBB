.. role:: python(code)
    :language: python
    :class: highlight

|

To obtain charts, make sure to add :python:`chart = True` as the last parameter.

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
etf.ln(
    name: str,
    chart: bool = False,
) -> Dict
{{< /highlight >}}

.. raw:: html

    <p>
    Return a selection of ETFs based on name filtered by total assets. [Source: Finance Database]
    </p>

* **Parameters**

    name: str
        Search by name to find ETFs matching the criteria.
    chart: bool
       Flag to display chart


* **Returns**

    data : Dict
        Dictionary with ETFs that match a certain name

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
etf.ln(
    name: str,
    limit: int = 10,
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display a selection of ETFs based on name filtered by total assets. [Source: Finance Database]
    </p>

* **Parameters**

    name: str
        Search by name to find ETFs matching the criteria.
    limit: int
        Limit of ETFs to display
    export: str
        Type of format to export data
    chart: bool
       Flag to display chart

