.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Scrape data for us bonds
    </h3>

{{< highlight python >}}
economy.usbonds() -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Returns**

    bonds: *pd.DataFrame*
        Dataframe containing name, coupon rate, yield and change in yield
   