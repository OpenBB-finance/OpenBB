.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Scrape data for global currencies
    </h3>

{{< highlight python >}}
economy.currencies() -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Returns**

    currencies: *pd.DataFrame*
        Dataframe containing name, price, net change and percent change
    