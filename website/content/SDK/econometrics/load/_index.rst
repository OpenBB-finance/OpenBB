.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
econometrics.load(
    file: str,
    file_types: Optional[List[str]] = None,
    data_files: Optional[Dict[Any, Any]] = None,
    data_examples: Optional[Dict[Any, Any]] = None,
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
    data_examples: *dict*
        Contains all available examples from Statsmodels

* **Returns**

    pd.DataFrame:
        Dataframe with custom data
