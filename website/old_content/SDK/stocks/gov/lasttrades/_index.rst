.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.gov.lasttrades(
    gov_type: str = 'congress',
    limit: int = -1,
    representative: str = '',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get last government trading [Source: quiverquant.com]
    </p>

* **Parameters**

    gov_type: str
        Type of government data between: congress, senate and house
    limit: int
        Number of days to look back
    representative: str
        Specific representative to look at

* **Returns**

    pd.DataFrame
        Last government trading
