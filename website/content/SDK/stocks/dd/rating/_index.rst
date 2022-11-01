.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get ratings for a given ticker. [Source: Financial Modeling Prep]
    </h3>

{{< highlight python >}}
stocks.dd.rating(
    symbol: str
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Stock ticker symbol

    
* **Returns**

    pd.DataFrame
        Rating data
    