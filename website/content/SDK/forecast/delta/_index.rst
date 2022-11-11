.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
forecast.delta(
    dataset: pandas.core.frame.DataFrame,
    target_column: str = 'close',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Calculate the %change of a variable based on a specific column
    </p>
