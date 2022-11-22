.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
alt.covid.global_cases(
    country: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get historical cases for given country
    </p>

* **Parameters**

    country: str
        Country to search for

* **Returns**

    pd.DataFrame
        Dataframe of historical cases
