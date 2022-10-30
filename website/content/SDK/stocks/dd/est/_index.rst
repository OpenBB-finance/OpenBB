.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get analysts' estimates for a given ticker. [Source: Business Insider]
    </h3>

{{< highlight python >}}
stocks.dd.est(
    symbol: str,
    ) -> Tuple[pandas.core.frame.DataFrame, pandas.core.frame.DataFrame, pandas.core.frame.DataFrame]
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Ticker to get analysts' estimates

    
* **Returns**

    df\_year\_estimates : *pd.DataFrame*
        Year estimates
    df\_quarter\_earnings : *pd.DataFrame*
        Quarter earnings estimates
    df\_quarter\_revenues : *pd.DataFrame*
        Quarter revenues estimates
    