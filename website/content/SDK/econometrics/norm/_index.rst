.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > The distribution of returns and generate statistics on the relation to the normal curve.
    This function calculates skew and kurtosis (the third and fourth moments) and performs both
    a Jarque-Bera and Shapiro Wilk test to determine if data is normally distributed.
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
econometrics.norm(
    data: pandas.core.series.Series,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    data : *pd.Series*
        A series or column of a DataFrame to test normality for

    
* **Returns**

    pd.DataFrame
        Dataframe containing statistics of normality
    