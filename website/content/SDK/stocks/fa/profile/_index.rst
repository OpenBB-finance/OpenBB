.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get ticker profile from FMP
    </h3>

{{< highlight python >}}
stocks.fa.profile(
    symbol: str,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Stock ticker symbol

* **Returns**

    pd.DataFrame:
        Dataframe of ticker profile
