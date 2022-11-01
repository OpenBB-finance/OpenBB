.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get alpha vantage company overview
    </h3>

{{< highlight python >}}
stocks.fa.av_overview(
    symbol: str
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Stock ticker symbol

    
* **Returns**

    pd.DataFrame
        Dataframe of fundamentals
    