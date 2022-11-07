.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.fa.info(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Gets ticker symbol info
    </p>

* **Parameters**

    symbol: str
        Stock ticker symbol

* **Returns**

    pd.DataFrame
        DataFrame of yfinance information
