.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get bitcoin price data
    [Price data from source: https://glassnode.com]
    [Inspired by: https://blockchaincenter.net]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.dd.btcrb(
    start\_date: str = '2010-01-01', end\_date: str = '2022-10-30', chart: bool = False,
    )
{{< /highlight >}}

* **Parameters**

    start\_date : *str*
        Initial date, format YYYY-MM-DD
    end\_date : *str*
        Final date, format YYYY-MM-DD
    