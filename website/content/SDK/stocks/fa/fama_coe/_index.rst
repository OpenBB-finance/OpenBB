.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Use Fama and French to get the cost of equity for a company
    </h3>

{{< highlight python >}}
stocks.fa.fama_coe(
    symbol: str
) -> float
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        The ticker symbol to be analyzed

    
* **Returns**

    coef : *float*
        The stock's Fama French coefficient
    