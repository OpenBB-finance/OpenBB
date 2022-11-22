.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.qa.capm_information(
    symbol: str,
    chart: bool = False,
) -> Tuple[float, float]
{{< /highlight >}}

.. raw:: html

    <p>
    Provides information that relates to the CAPM model
    </p>

* **Parameters**

    symbol : str
        A ticker symbol in string form

* **Returns**

    beta : float
        The beta for a stock
    sys : float
        The systematic risk for a stock
