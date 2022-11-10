.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.fa.fama_coe(
    symbol: str,
    chart: bool = False,
) -> float
{{< /highlight >}}

.. raw:: html

    <p>
    Use Fama and French to get the cost of equity for a company
    </p>

* **Parameters**

    symbol : str
        The ticker symbol to be analyzed

* **Returns**

    coef : float
        The stock's Fama French coefficient
