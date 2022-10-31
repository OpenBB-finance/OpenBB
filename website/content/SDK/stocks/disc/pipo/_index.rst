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
    num_days_behind: int = 5,
    start_date: Optional[str] = None,
    )
{{< /highlight >}}

* **Parameters**

    num_days_behind: *int*
        Number of days to look behind for IPOs dates
    start_date: *str*
        The starting date (format YYYY-MM-DD) to look for IPOs
    