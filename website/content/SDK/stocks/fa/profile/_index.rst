.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.fa.profile(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get ticker profile from FMP
    </p>

* **Parameters**

    symbol : str
        Stock ticker symbol

* **Returns**

    pd.DataFrame:
        Dataframe of ticker profile
