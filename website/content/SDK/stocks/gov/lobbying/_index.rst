.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Corporate lobbying details
    </h3>

{{< highlight python >}}
stocks.gov.lobbying(
    symbol: str,
    limit: int = 10,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Ticker symbol to get corporate lobbying data from
    limit: *int*
        Number of events to show

    
* **Returns**

    pd.DataFrame
        Dataframe with corporate lobbying data
   