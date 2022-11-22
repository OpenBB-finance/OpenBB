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
common.qa.summary(
    data: pandas.core.frame.DataFrame,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Print summary statistics
    </p>

* **Parameters**

    data : pd.DataFrame
        Dataframe to get summary statistics for
    chart: bool
       Flag to display chart


* **Returns**

    summary : pd.DataFrame
        Summary statistics

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
common.qa.summary(
    data: pandas.core.frame.DataFrame,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Show summary statistics
    </p>

* **Parameters**

    data : pd.DataFrame
        DataFrame to get statistics of
    export : str
        Format to export data
    chart: bool
       Flag to display chart

