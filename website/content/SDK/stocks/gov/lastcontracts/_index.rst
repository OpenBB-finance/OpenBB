.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get last government contracts [Source: quiverquant.com]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.gov.lastcontracts(
    past\_transaction\_days: int = 2,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    past\_transaction\_days: *int*
        Number of days to look back

    
* **Returns**

    pd.DataFrame
        DataFrame of government contracts
    