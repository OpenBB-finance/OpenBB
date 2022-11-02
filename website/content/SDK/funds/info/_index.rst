.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > 
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
funds.info(
    name: str,
    country: str = 'united states',
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    name: *str*
        Name of fund (not symbol) to get information
    country: *str*
        Country of fund
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        Dataframe of fund information
