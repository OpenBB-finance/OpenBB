.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.disc.pipo(
    num_days_behind: int = 5,
    start_date: Optional[str] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Past IPOs dates. [Source: Finnhub]
    </p>

* **Parameters**

    num_days_behind: int
        Number of days to look behind for IPOs dates
    start_date: str
        The starting date (format YYYY-MM-DD) to look for IPOs
