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
    num\_days\_ahead: int = 5,
    end\_date: Optional[str] = None,
    )
{{< /highlight >}}

* **Parameters**

    num\_days\_ahead: *int*
        Number of days to look ahead for IPOs dates
    end\_date: *datetime*
        The end date (format YYYY-MM-DD) to look for IPOs from today onwards
    