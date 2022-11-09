.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.fa.hq(
    symbol: str,
    chart: bool = False,
) -> str
{{< /highlight >}}

.. raw:: html

    <p>
    Gets google map url for headquarter
    </p>

* **Parameters**

    symbol: str
        Stock ticker symbol

* **Returns**

    str
        Headquarter google maps url
