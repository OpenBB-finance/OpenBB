.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
forecast.combine(
    df1: pandas.core.frame.DataFrame,
    df2: pandas.core.frame.DataFrame,
    column: str,
    dataset: str = '',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Adds the given column of df2 to df1
    </p>

* **Parameters**

    df1: pd.DataFrame
        The dataframe to add a column to
    df2: pd.DataFrame
        The dataframe to lose a column
    column: str
        The column to transfer
    dataset: str
        A name for df2 (shows in name of new column)

* **Returns**

    data: pd.DataFrame
        The new dataframe
