.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get sustainability metrics from yahoo
    </h3>

{{< highlight python >}}
stocks.fa.sust(
    symbol: str,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Stock ticker symbol

* **Returns**

    pd.DataFrame
        Dataframe of sustainability metrics
