.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Future IPOs dates. [Source: Finnhub]
    </h3>

{{< highlight python >}}
stocks.disc.fipo(
    num_days_ahead: int = 5,
    end_date: Optional[str] = None,
)
{{< /highlight >}}

* **Parameters**

    num_days_ahead: *int*
        Number of days to look ahead for IPOs dates
    end_date: *datetime*
        The end date (format YYYY-MM-DD) to look for IPOs from today onwards
    