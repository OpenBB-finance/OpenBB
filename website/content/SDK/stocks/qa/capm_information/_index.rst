.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Provides information that relates to the CAPM model
    </h3>

{{< highlight python >}}
stocks.qa.capm_information(
    symbol: str,
) -> Tuple[float, float]
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        A ticker symbol in string form

    
* **Returns**

    beta : *float*
        The beta for a stock
    sys : *float*
        The systematic risk for a stock
   