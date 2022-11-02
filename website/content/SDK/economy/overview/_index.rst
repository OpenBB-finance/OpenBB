.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Scrape data for market overview
    </h3>

{{< highlight python >}}
economy.overview() -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Returns**

    overview: *pd.DataFrame*
        Dataframe containing name, price, net change and percent change
