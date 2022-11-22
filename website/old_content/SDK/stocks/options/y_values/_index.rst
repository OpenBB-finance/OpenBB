.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.options.y_values(
    base: float,
    price: float,
    options: List[Dict[Any, Any]],
    underlying: int,
    chart: bool = False,
) -> float
{{< /highlight >}}

.. raw:: html

    <p>
    Generates y values for corresponding x value
    </p>
