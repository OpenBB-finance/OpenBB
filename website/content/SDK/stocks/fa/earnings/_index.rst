.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get earnings calendar for ticker
    </h3>

{{< highlight python >}}
stocks.fa.earnings(
    symbol: str,
    quarterly: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Stock ticker symbol
    quarterly : bool, optional
        Flag to get quarterly and not annual, by default False

    
* **Returns**

    pd.DataFrame
        Dataframe of earnings
    