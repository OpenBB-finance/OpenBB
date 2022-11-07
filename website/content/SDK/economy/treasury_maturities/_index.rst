.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
economy.treasury_maturities() -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get treasury maturity options [Source: EconDB]
    </p>

* **Returns**

    df: pd.DataFrame
        Contains the name of the instruments and a string containing all options.
