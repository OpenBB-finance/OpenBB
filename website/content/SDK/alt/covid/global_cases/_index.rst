.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get historical cases for given country
    </h3>

{{< highlight python >}}
alt.covid.global_cases(
    country: str,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    country: *str*
        Country to search for

    
* **Returns**

    pd.DataFrame
        Dataframe of historical cases
   