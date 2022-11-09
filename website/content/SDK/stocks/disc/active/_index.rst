.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.disc.active() -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get stocks ordered in descending order by intraday trade volume. [Source: Yahoo Finance]
    </p>

* **Returns**

    pd.DataFrame
        Most active stocks
