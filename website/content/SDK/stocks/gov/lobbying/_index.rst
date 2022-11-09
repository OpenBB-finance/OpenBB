.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.gov.lobbying(
    symbol: str,
    limit: int = 10,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Corporate lobbying details
    </p>

* **Parameters**

    symbol: str
        Ticker symbol to get corporate lobbying data from
    limit: int
        Number of events to show

* **Returns**

    pd.DataFrame
        Dataframe with corporate lobbying data
