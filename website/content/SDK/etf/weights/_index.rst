.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Return sector weightings allocation of ETF. [Source: Yahoo Finance]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
etf.weights(
    name: str,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> Dict
{{< /highlight >}}

* **Parameters**

    name: *str*
        ETF name
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    Dict
        Dictionary with sector weightings allocation
