.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.qa.fama_raw() -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Gets base Fama French data to calculate risk
    </p>

* **Returns**

    fama : pd.DataFrame
        A data with fama french model information
