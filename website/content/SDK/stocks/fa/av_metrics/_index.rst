.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.fa.av_metrics(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get key metrics from overview
    </p>

* **Parameters**

    symbol : str
        Stock ticker symbol

* **Returns**

    pd.DataFrame
        Dataframe of key metrics
