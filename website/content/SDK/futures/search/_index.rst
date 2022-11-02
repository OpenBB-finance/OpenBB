.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get search futures [Source: Yahoo Finance]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
futures.search(
    category: str = '',
    exchange: str = '',
    description: str = '',
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
)
{{< /highlight >}}

* **Parameters**

    category: *str*
        Select the category where the future exists
    exchange: *str*
        Select the exchange where the future exists
    description: *str*
        Select the description where the future exists
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot
