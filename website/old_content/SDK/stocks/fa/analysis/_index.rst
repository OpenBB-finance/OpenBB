.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.fa.analysis(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Save time reading SEC filings with the help of machine learning. [Source: https://eclect.us]
    </p>

* **Parameters**

    symbol: str
        Ticker symbol to see analysis of filings

* **Returns**

    str
        Analysis of filings text
