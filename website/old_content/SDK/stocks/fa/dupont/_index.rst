.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.fa.dupont(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get dupont ratios
    </p>

* **Parameters**

    symbol : str
        Stock ticker symbol

* **Returns**

    dupont : pd.DataFrame
        The dupont ratio breakdown
