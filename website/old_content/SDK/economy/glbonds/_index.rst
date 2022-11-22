.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
economy.glbonds() -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Scrape data for global bonds
    </p>

* **Returns**

    bonds: pd.DataFrame
        Dataframe containing name, coupon rate, yield and change in yield
