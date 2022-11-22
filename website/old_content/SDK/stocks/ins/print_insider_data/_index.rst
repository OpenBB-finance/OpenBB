.. role:: python(code)
    :language: python
    :class: highlight

|

To obtain charts, make sure to add :python:`chart = True` as the last parameter.

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.ins.print_insider_data(
    type_insider: str = 'lcb',
    limit: int = 10,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Print insider data
    </p>

* **Parameters**

    type_insider: str
        Insider type of data. Available types can be accessed through get_insider_types().
    limit: int
        Limit of data rows to display
    chart: bool
       Flag to display chart


|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.ins.print_insider_data(
    type_insider: str = 'lcb',
    limit: int = 10,
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Print insider data
    </p>

* **Parameters**

    type_insider: str
        Insider type of data. Available types can be accessed through get_insider_types().
    limit: int
        Limit of data rows to display
    export: str
        Export data format
    chart: bool
       Flag to display chart

