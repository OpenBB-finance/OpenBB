.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Return a selection of ETFs based on name filtered by total assets. [Source: Finance Database]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
etf.ln(
    name: str,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> Dict
{{< /highlight >}}

* **Parameters**

    name: *str*
        Search by name to find ETFs matching the criteria.
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    data : *Dict*
        Dictionary with ETFs that match a certain name
