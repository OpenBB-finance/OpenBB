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
funds.info(
    name: str,
    country: str = 'united states',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    
    </p>

* **Parameters**

    name: *str*
        Name of fund (not symbol) to get information
    country: *str*
        Country of fund
    chart: *bool*
       Flag to display chart


* **Returns**

    pd.DataFrame
        Dataframe of fund information

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
funds.info(
    name: str,
    country: str = 'united states',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display fund information.  Finds name from symbol first if name is false
    </p>

* **Parameters**

    name: *str*
        Fund name to get info for
    country : *str*
        Country of fund
    chart: *bool*
       Flag to display chart

