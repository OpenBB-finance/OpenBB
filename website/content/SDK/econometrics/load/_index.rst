.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Load custom file into dataframe.
    </h3>

{{< highlight python >}}
econometrics.load(
    file: str,
    file\_types: Optional[List[str]] = None,
    data\_files: Optional[Dict[Any, Any]] = None,
    data\_examples: Optional[Dict[Any, Any]] = None,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

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
    