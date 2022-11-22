.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.fa.divs(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get historical dividend for ticker
    </p>

* **Parameters**

    symbol: str
        Ticker symbol to get dividend for

* **Returns**

    pd.DataFrame:
        Dataframe of dividends and dates
