.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get similar companies from Finviz
    </h3>

{{< highlight python >}}
stocks.ca.finviz_peers(
    symbol: str,
    compare_list: List[str] = None,
    ) -> Tuple[List[str], str]
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Ticker to find comparisons for
    compare_list : List[str]
        List of fields to compare, ["Sector", "Industry", "Country"]

    
* **Returns**

    List[str]
        List of similar companies
    