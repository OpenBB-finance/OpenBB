.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Obtain columns-dataset combinations from loaded in datasets that can be used in other commands
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
econometrics.options(
    datasets: Dict[str, pandas.core.frame.DataFrame],
    dataset\_name: str = '',
    chart: bool = False,
    ) -> Dict[Union[str, Any], pandas.core.frame.DataFrame]
{{< /highlight >}}

* **Parameters**

    datasets: *dict*
        The available datasets.
    dataset\_name: *str*
        The dataset you wish to show the options for.

    
* **Returns**

    option\_tables: *dict*
        A dictionary with a DataFrame for each option. With dataset\_name set, only shows one
        options table.
    