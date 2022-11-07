.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
economy.futures() -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Scrape data for top commodities
    </p>

* **Returns**

    commodities: pd.DataFrame
        Dataframe containing name, price, net change and percent change
