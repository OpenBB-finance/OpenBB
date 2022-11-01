.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Load cases and find slope over period
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
alt.covid.slopes(
    days_back: int = 30,
    limit: int = 50,
    threshold: int = 10000,
    ascend: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    days_back: *int*
        Number of historical days to consider
    limit: *int*
        Number of rows to show
    threshold: *int*
        Threshold for total number of cases
    ascend: *bool*
        Flag to sort in ascending order

    
* **Returns**

    pd.DataFrame
        Dataframe containing slopes

    
* **Examples**

    {{< highlight python >}}
    >>> from openbb_terminal.sdk import openbb

    ### Get the data
    df = openbb.alt.covid.slopes(chart = False)

    ### Get the chart
    openbb.alt.covid.slopes(chart = True)
    {{< /highlight >}}