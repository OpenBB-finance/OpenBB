.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Load in the Excel file to determine the allocation that needs to be set.
    </h3>

{{< highlight python >}}
portfolio.po.load(
    excel_file: str = ''
)
{{< /highlight >}}

* **Parameters**

    excel_file: *str*
        The location of the Excel file that needs to be loaded.

    
* **Returns**

    tickers: *list*
        Returns a list with ticker symbols
    categories: *dictionary*
        Returns a dictionary that specifies each category
    