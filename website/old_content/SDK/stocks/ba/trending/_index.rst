.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.ba.trending() -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get trending tickers from stocktwits [Source: stocktwits]
    </p>

* **Returns**

    pd.DataFrame
        Dataframe of trending tickers and watchlist count
