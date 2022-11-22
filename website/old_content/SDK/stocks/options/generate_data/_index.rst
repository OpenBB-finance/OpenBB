.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.options.generate_data(
    current_price: float,
    options: List[Dict[str, int]],
    underlying: int,
    chart: bool = False,
) -> Tuple[List[float], List[float], List[float]]
{{< /highlight >}}

.. raw:: html

    <p>
    Gets x values, and y values before and after premium
    </p>
