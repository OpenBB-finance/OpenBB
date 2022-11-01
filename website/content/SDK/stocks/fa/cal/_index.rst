.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get calendar earnings for ticker symbol
    </h3>

{{< highlight python >}}
stocks.fa.cal(
    symbol: str,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Stock ticker symbol

    
* **Returns**

    pd.DataFrame
        Dataframe of calendar earnings
    