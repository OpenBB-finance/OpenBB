.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get similar companies from Finhub
    </h3>

{{< highlight python >}}
stocks.ca.finnhub_peers(
    symbol: str,
) -> List[str]
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Ticker to find comparisons for

    
* **Returns**

    List[str]
        List of similar companies
    