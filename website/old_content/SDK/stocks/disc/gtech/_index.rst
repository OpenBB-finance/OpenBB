.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.disc.gtech() -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get technology stocks with revenue and earnings growth in excess of 25%. [Source: Yahoo Finance]
    </p>

* **Returns**

    pd.DataFrame
        Growth technology stocks
