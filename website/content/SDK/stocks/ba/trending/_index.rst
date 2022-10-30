.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get trending tickers from stocktwits [Source: stocktwits]
    </h3>

{{< highlight python >}}
stocks.ba.trending(
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Returns**

    pd.DataFrame
        Dataframe of trending tickers and watchlist count
    