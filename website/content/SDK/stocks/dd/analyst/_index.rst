.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.dd.analyst(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get analyst data. [Source: Finviz]
    </p>

* **Parameters**

    symbol : str
        Stock ticker symbol

* **Returns**

    df_fa: DataFrame
        Analyst price targets
