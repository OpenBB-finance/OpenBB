.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get historical dividend for ticker
    </h3>

{{< highlight python >}}
stocks.fa.divs(
    symbol: str,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Ticker symbol to get dividend for

    
* **Returns**

    pd.DataFrame:
        Dataframe of dividends and dates
    