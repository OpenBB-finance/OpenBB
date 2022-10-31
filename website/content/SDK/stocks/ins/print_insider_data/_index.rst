.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Print insider data
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.ins.print_insider_data(
    type_insider: str = 'lcb',
    limit: int = 10,
    chart: bool = False,
    )
{{< /highlight >}}

* **Parameters**

    type_insider: *str*
        Insider type of data. Available types can be accessed through get_insider_types().
    limit: *int*
        Limit of data rows to display
    