.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get similar companies from Polygon
    </h3>

{{< highlight python >}}
stocks.ca.polygon_peers(
    symbol: str,
    us\_only: bool = False,
    ) -> List[str]
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Ticker to get similar companies of
    us\_only: *bool*
        Only stocks from the US stock exchanges

    
* **Returns**

    List[str]:
        List of similar tickers
    