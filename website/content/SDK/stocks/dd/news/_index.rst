.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get news from Finviz
    </h3>

{{< highlight python >}}
stocks.dd.news(
    symbol: str,
) -> List[Any]
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Stock ticker symbol

    
* **Returns**

    List[Any]
        News
   