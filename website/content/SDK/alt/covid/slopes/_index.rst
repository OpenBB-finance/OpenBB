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
alt.covid.slopes(
    days_back: int = 30,
    limit: int = 50,
    threshold: int = 10000,
    ascend: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Load cases and find slope over period
    </p>

* **Parameters**

    days_back: int
        Number of historical days to consider
    limit: int
        Number of rows to show
    threshold: int
        Threshold for total number of cases
    ascend: bool
        Flag to sort in ascending order
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Dataframe containing slopes

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
alt.covid.slopes(
    days_back: int = 30,
    limit: int = 10,
    threshold: int = 10000,
    ascend: bool = False,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    
    </p>

* **Parameters**

    days_back: int
        Number of historical days to get slope for
    limit: int
        Number to show in table
    ascend: bool
        Flag to sort in ascending order
    threshold: int
        Threshold for total cases over period
    export : str
        Format to export data
    chart: bool
       Flag to display chart

