.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.fa.fmp_metrics(
    symbol: str,
    limit: int = 5,
    quarterly: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get key metrics
    </p>

* **Parameters**

    symbol : str
        Stock ticker symbol
    limit : int
        Number to get
    quarterly : bool, optional
        Flag to get quarterly data, by default False

* **Returns**

    pd.DataFrame
        Dataframe of key metrics
