.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get list of all available coins on CoinPaprika  [Source: CoinPaprika]
    </h3>

{{< highlight python >}}
crypto.ov.list_of_coins() -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Returns**

    pandas.DataFrame
        Available coins on CoinPaprika
        rank, id, name, symbol, type
