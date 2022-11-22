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
funds.overview(
    country: str = 'united states',
    limit: int = 20,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    
    </p>

* **Parameters**

    country: *str*
        Country to get overview for
    limit: *int*
        Number of results to get
    chart: *bool*
       Flag to display chart


* **Returns**

    pd.DataFrame
        Dataframe containing overview

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
funds.overview(
    country: str = 'united states',
    limit: int = 10,
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Displays an overview of the main funds from a country.
    </p>

* **Parameters**

    country: *str*
        Country to get overview for
    limit: *int*
        Number to show
    export : *str*
        Format to export data
    chart: *bool*
       Flag to display chart

