.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.ca.finviz_peers(
    symbol: str,
    compare_list: List[str] = None,
    chart: bool = False,
) -> Tuple[List[str], str]
{{< /highlight >}}

.. raw:: html

    <p>
    Get similar companies from Finviz
    </p>

* **Parameters**

    symbol : str
        Ticker to find comparisons for
    compare_list : List[str]
        List of fields to compare, ["Sector", "Industry", "Country"]

* **Returns**

    List[str]
        List of similar companies
