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
etf.summary(
    name: str,
    chart: bool = False,
) -> str
{{< /highlight >}}

.. raw:: html

    <p>
    Return summary description of ETF. [Source: Yahoo Finance]
    </p>

* **Parameters**

    name: str
        ETF name
    chart: bool
       Flag to display chart


* **Returns**

    str
        Summary description of the ETF

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
etf.summary(
    name: str,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display ETF description summary. [Source: Yahoo Finance]
    </p>

* **Parameters**

    name: str
        ETF name
    chart: bool
       Flag to display chart

