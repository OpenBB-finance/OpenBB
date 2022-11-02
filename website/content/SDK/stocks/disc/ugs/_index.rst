.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.disc.ugs() -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get stocks with earnings growth rates better than 25% and relatively low PE and PEG ratios.
    [Source: Yahoo Finance]
    </p>

* **Returns**

    pd.DataFrame
        Undervalued stocks
