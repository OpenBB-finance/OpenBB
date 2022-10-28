.. role:: python(code)
    :language: python
    :class: highlight

|

> Get historical deaths for given country
------------------------------------------
{{< highlight python >}}
alt.covid.global_deaths(country: str) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    country: *str*
        Country to search for

    
* **Returns**

    pd.DataFrame
        Dataframe of historical deaths
    