.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Search investpy for matching funds
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
funds.search(
    by: str = 'name',
    value: str = '',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    by : *str*
        Field to match on.  Can be name, issuer, isin or symbol
    value : *str*
        String that will be searched for

    
* **Returns**

    pd.DataFrame
        Dataframe containing matches
    