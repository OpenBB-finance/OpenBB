.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Return summary description of ETF. [Source: Yahoo Finance]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
etf.summary(
    name: str,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> str
{{< /highlight >}}

* **Parameters**

    name: *str*
        ETF name
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    str
        Summary description of the ETF
