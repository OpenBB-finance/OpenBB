.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
economy.indices() -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get the top US indices
    </p>

* **Returns**

    indices: pd.DataFrame
        Dataframe containing name, price, net change and percent change
