.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get dupont ratios
    </h3>

{{< highlight python >}}
stocks.fa.dupont(
    symbol: str,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Stock ticker symbol

    
* **Returns**

    dupont : *pd.DataFrame*
        The dupont ratio breakdown
   