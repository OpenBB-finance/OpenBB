.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get analyst data. [Source: Finviz]
    </h3>

{{< highlight python >}}
stocks.dd.analyst(
    symbol: str
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Stock ticker symbol

    
* **Returns**

    df_fa: *DataFrame*
        Analyst price targets
    