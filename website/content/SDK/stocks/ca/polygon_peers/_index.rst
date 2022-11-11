.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.ca.polygon_peers(
    symbol: str,
    us_only: bool = False,
    chart: bool = False,
) -> List[str]
{{< /highlight >}}

.. raw:: html

    <p>
    Get similar companies from Polygon
    </p>

* **Parameters**

    symbol: str
        Ticker to get similar companies of
    us_only: bool
        Only stocks from the US stock exchanges

* **Returns**

    List[str]:
        List of similar tickers
