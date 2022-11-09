.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.disc.asc() -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get Yahoo Finance small cap stocks with earnings growth rates better than 25%.
    [Source: Yahoo Finance]
    </p>

* **Returns**

    pd.DataFrame
        Most aggressive small cap stocks
