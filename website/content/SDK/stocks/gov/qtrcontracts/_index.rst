.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Analyzes quarterly contracts by ticker
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.gov.qtrcontracts(
    analysis: str = 'total',
    limit: int = 5,
    chart: bool = False
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    analysis : *str*
        How to analyze.  Either gives total amount or sorts by high/low momentum.
    limit : int, optional
        Number to return, by default 5

    
* **Returns**

    pd.DataFrame
        Dataframe with tickers and total amount if total selected.
    