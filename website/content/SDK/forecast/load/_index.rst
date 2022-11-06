.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
forecast.load(
    file: str,
    file_types: Optional[List[str]] = None,
    data_files: Optional[Dict[Any, Any]] = None,
    add_extension: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Load custom file into dataframe.
    </p>

* **Parameters**

    file: *str*
        Path to file
    file_types: *list*
        Supported file types
    data_files: *dict*
        Contains all available data files within the Export folder
    add_extension:
        Takes a file name and tries loading with csv or xlsx extension

* **Returns**

    pd.DataFrame:
        Dataframe with custom data
