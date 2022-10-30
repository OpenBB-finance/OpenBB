.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns today hot penny stocks
    </h3>

{{< highlight python >}}
stocks.disc.hotpenny(
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Returns**

    DataFrame
        Today hot penny stocks DataFrame with the following columns:
        Ticker, Price, Change, $ Volume, Volume, # Trades
    