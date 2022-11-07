.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.fa.website(
    symbol: str,
    chart: bool = False,
) -> str
{{< /highlight >}}

.. raw:: html

    <p>
    Gets website of company from yfinance
    </p>

* **Parameters**

    symbol: str
        Stock ticker symbol

* **Returns**

    str
        Company websit
