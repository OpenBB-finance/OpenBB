.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Obtain columns-dataset combinations from loaded in datasets that can be used in other commands
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
econometrics.options(
    datasets: Dict[str, pandas.core.frame.DataFrame],
    dataset_name: str = '',
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> Dict[Union[str, Any], pandas.core.frame.DataFrame]
{{< /highlight >}}

* **Parameters**

    datasets: *dict*
        The available datasets.
    dataset_name: *str*
        The dataset you wish to show the options for.
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    option_tables: *dict*
        A dictionary with a DataFrame for each option. With dataset_name set, only shows one
        options table.
