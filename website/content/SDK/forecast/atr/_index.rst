.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
forecast.atr(
    dataset: pandas.core.frame.DataFrame,
    close_column: str = 'close',
    high_column: str = 'high',
    low_column: str = 'low',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Calculate the Average True Range of a variable based on a a specific stock ticker.
    </p>
