.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.po.load(
    excel_file: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Load in the Excel file to determine the allocation that needs to be set.
    </p>

* **Parameters**

    excel_file: str
        The location of the Excel file that needs to be loaded.

* **Returns**

    tickers: list
        Returns a list with ticker symbols
    categories: dictionary
        Returns a dictionary that specifies each category
