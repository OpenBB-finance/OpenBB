.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get stocks with earnings growth rates better than 25% and relatively low PE and PEG ratios.
    [Source: Yahoo Finance]
    </h3>

{{< highlight python >}}
stocks.disc.ugs() -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Returns**

    pd.DataFrame
        Undervalued stocks
   