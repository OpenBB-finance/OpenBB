.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.qa.historical_5(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get 5 year monthly historical performance for a ticker with dividends filtered
    </p>

* **Parameters**

    symbol : str
        A ticker symbol in string form

* **Returns**

    data : pd.DataFrame
        A dataframe with historical information
