.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get key metrics from overview
    </h3>

{{< highlight python >}}
stocks.fa.av_metrics(
    symbol: str,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Stock ticker symbol

    
* **Returns**

    pd.DataFrame
        Dataframe of key metrics
    