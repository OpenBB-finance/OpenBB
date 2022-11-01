.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > 
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
funds.overview(
    country: str = 'united states',
    limit: int = 20,
    chart: bool = False
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    country: *str*
        Country to get overview for
    limit: *int*
        Number of results to get

    
* **Returns**

    pd.DataFrame
        Dataframe containing overview
    