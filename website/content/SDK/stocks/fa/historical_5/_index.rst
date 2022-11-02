.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get 5 year monthly historical performance for a ticker with dividends filtered
    </h3>

{{< highlight python >}}
stocks.fa.historical_5(
    symbol: str,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        The ticker symbol to be analyzed

* **Returns**

    df: *pd.DataFrame*
        Historical data
