.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get the top US indices
    </h3>

{{< highlight python >}}
economy.indices() -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Returns**

    indices: *pd.DataFrame*
        Dataframe containing name, price, net change and percent change
