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
econometrics.options(
    datasets: Dict[str, pandas.core.frame.DataFrame],
    dataset_name: str = '',
    chart: bool = False,
) -> Dict[Union[str, Any], pandas.core.frame.DataFrame]
{{< /highlight >}}

.. raw:: html

    <p>
    Obtain columns-dataset combinations from loaded in datasets that can be used in other commands
    </p>

* **Parameters**

    datasets: dict
        The available datasets.
    dataset_name: str
        The dataset you wish to show the options for.
    chart: bool
       Flag to display chart


* **Returns**

    option_tables: dict
        A dictionary with a DataFrame for each option. With dataset_name set, only shows one
        options table.

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
econometrics.options(
    datasets: Dict[str, pandas.core.frame.DataFrame],
    dataset_name: str = None,
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Plot custom data
    </p>

* **Parameters**

    datasets: dict
        The loaded in datasets
    dataset_name: str
        The name of the dataset you wish to show options for
    export: str
        Format to export image
    chart: bool
       Flag to display chart

