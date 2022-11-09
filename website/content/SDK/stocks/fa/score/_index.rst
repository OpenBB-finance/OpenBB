.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.fa.score(
    symbol: str,
    chart: bool = False,
) -> Optional[numpy.number]
{{< /highlight >}}

.. raw:: html

    <p>
    Gets value score from fmp
    </p>

* **Parameters**

    symbol : str
        Stock ticker symbol

* **Returns**

    np.number
        Value score
