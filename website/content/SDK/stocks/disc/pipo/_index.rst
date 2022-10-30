.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Past IPOs dates. [Source: Finnhub]
    </h3>

{{< highlight python >}}
stocks.disc.pipo(
    num\_days\_behind: int = 5,
    start\_date: Optional[str] = None,
    )
{{< /highlight >}}

* **Parameters**

    num\_days\_behind: *int*
        Number of days to look behind for IPOs dates
    start\_date: *str*
        The starting date (format YYYY-MM-DD) to look for IPOs
    