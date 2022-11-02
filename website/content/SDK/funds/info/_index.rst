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
funds.info(
    name: str,
    country: str = 'united states',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    name: *str*
        Name of fund (not symbol) to get information
    country: *str*
        Country of fund

    
* **Returns**

    pd.DataFrame
        Dataframe of fund information
   