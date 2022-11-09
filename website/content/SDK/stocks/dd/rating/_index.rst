.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.dd.rating(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get ratings for a given ticker. [Source: Financial Modeling Prep]
    </p>

* **Parameters**

    symbol : str
        Stock ticker symbol

* **Returns**

    pd.DataFrame
        Rating data
