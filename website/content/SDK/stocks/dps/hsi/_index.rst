.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.dps.hsi() -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Returns a high short interest DataFrame
    </p>

* **Returns**

    DataFrame
        High short interest Dataframe with the following columns:
        Ticker, Company, Exchange, ShortInt, Float, Outstd, Industry
