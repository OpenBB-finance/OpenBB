.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.dd.news(
    symbol: str,
    chart: bool = False,
) -> List[Any]
{{< /highlight >}}

.. raw:: html

    <p>
    Get news from Finviz
    </p>

* **Parameters**

    symbol : str
        Stock ticker symbol

* **Returns**

    List[Any]
        News
