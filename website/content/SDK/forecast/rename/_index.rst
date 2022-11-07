.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
forecast.rename(
    data: pandas.core.frame.DataFrame,
    old_column: str,
    new_column: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Rename a column in a dataframe
    </p>

* **Parameters**

    data: pd.DataFrame
        The dataframe to have a column renamed
    old_column: str
        The column that will have its name changed
    new_column: str
        The name to update to

* **Returns**

    new_df: pd.DataFrame
        The dataframe with the renamed column
