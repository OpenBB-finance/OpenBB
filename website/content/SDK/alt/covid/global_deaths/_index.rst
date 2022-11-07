.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
alt.covid.global_deaths(
    country: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get historical deaths for given country
    </p>

* **Parameters**

    country: str
        Country to search for

* **Returns**

    pd.DataFrame
        Dataframe of historical deaths
