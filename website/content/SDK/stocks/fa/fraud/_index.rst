.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get fraud ratios based on fundamentals
    </h3>

{{< highlight python >}}
stocks.fa.fraud(
    symbol: str,
    detail: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Stock ticker symbol
    detail : *bool*
        Whether to provide extra m-score details

* **Returns**

    metrics : *pd.DataFrame*
        The fraud ratios
