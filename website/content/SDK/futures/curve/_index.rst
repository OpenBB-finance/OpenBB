.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get curve futures [Source: Yahoo Finance]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
futures.curve(
    ticker: str = '',
    chart: bool = False,
)
{{< /highlight >}}

* **Parameters**

    ticker: *str*
        Ticker to get forward curve
   