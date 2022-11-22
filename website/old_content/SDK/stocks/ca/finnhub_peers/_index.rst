.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.ca.finnhub_peers(
    symbol: str,
    chart: bool = False,
) -> List[str]
{{< /highlight >}}

.. raw:: html

    <p>
    Get similar companies from Finhub
    </p>

* **Parameters**

    symbol : str
        Ticker to find comparisons for

* **Returns**

    List[str]
        List of similar companies
