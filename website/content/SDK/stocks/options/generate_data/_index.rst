.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Gets x values, and y values before and after premium
    </h3>

{{< highlight python >}}
stocks.options.generate_data(
    current_price: float,
    options: List[Dict[str, int]],
    underlying: int,
) -> Tuple[List[float], List[float], List[float]]
{{< /highlight >}}

* **Parameters**

es before and after premiums