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
funds.search(
    by: str = 'name',
    value: str = '',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Search investpy for matching funds
    </p>

* **Parameters**

    by : *str*
        Field to match on.  Can be name, issuer, isin or symbol
    value : *str*
        String that will be searched for
    chart: *bool*
       Flag to display chart


* **Returns**

    pd.DataFrame
        Dataframe containing matches

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
funds.search(
    by: str = 'name',
    value: str = '',
    country: str = 'united states',
    limit: int = 10,
    sortby: str = '',
    ascend: bool = False,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display results of searching for Mutual Funds
    </p>

* **Parameters**

    by : *str*
        Field to match on.  Can be name, issuer, isin or symbol
    value : *str*
        String that will be searched for
    country: *str*
        Country to filter on
    limit: *int*
        Number to show
    sortby: *str*
        Column to sort by
    ascend: *bool*
        Flag to sort in ascending order
    chart: *bool*
       Flag to display chart

