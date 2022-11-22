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
stocks.ta.summary(
    symbol: str,
    chart: bool = False,
) -> str
{{< /highlight >}}

.. raw:: html

    <p>
    Get technical summary report provided by FinBrain's API
    </p>

* **Parameters**

    symbol : str
        Ticker symbol to get the technical summary
    chart: bool
       Flag to display chart


* **Returns**

    report:str
        technical summary report

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.ta.summary(
    symbol: str,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Print technical summary report provided by FinBrain's API
    </p>

* **Parameters**

    symbol: str
        Ticker symbol to get the technical summary
    chart: bool
       Flag to display chart

