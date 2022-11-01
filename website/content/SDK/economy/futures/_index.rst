.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Scrape data for top commodities
    </h3>

{{< highlight python >}}
economy.futures() -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Returns**

    commodities: *pd.DataFrame*
        Dataframe containing name, price, net change and percent change
    