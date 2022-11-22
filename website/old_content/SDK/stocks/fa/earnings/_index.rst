.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.fa.earnings(
    symbol: str,
    quarterly: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get earnings calendar for ticker
    </p>

* **Parameters**

    symbol : str
        Stock ticker symbol
    quarterly : bool, optional
        Flag to get quarterly and not annual, by default False

* **Returns**

    pd.DataFrame
        Dataframe of earnings
