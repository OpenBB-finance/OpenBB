.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
common.qa.decompose(
    data: pandas.core.frame.DataFrame,
    multiplicative: bool = False,
    chart: bool = False,
) -> Tuple[Any, pandas.core.frame.DataFrame, pandas.core.frame.DataFrame]
{{< /highlight >}}

.. raw:: html

    <p>
    Perform seasonal decomposition
    </p>

* **Parameters**

    data : pd.DataFrame
        Dataframe of targeted data
    multiplicative : bool
        Boolean to indicate multiplication instead of addition

* **Returns**

    result: Any
        Result of statsmodels seasonal_decompose
    cycle: pd.DataFrame
        Filtered cycle
    trend: pd.DataFrame
        Filtered Trend
