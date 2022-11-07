.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.fa.fraud(
    symbol: str,
    detail: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get fraud ratios based on fundamentals
    </p>

* **Parameters**

    symbol : str
        Stock ticker symbol
    detail : bool
        Whether to provide extra m-score details

* **Returns**

    metrics : pd.DataFrame
        The fraud ratios
