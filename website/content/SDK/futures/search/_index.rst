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
futures.search(
    category: str = '',
    exchange: str = '',
    description: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Get search futures [Source: Yahoo Finance]
    </p>

* **Parameters**

    category: str
        Select the category where the future exists
    exchange: str
        Select the exchange where the future exists
    description: str
        Select the description where the future exists
    chart: bool
       Flag to display chart


|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
futures.search(
    category: str = '',
    exchange: str = '',
    description: str = '',
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display search futures [Source: Yahoo Finance]
    </p>

* **Parameters**

    category: str
        Select the category where the future exists
    exchange: str
        Select the exchange where the future exists
    description: str
        Select the description of the future
    export: str
        Type of format to export data
    chart: bool
       Flag to display chart

