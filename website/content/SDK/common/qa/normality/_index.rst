.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Look at the distribution of returns and generate statistics on the relation to the normal curve.
    This function calculates skew and kurtosis (the third and fourth moments) and performs both
    a Jarque-Bera and Shapiro Wilk test to determine if data is normally distributed.
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
common.qa.normality(data: pandas.core.frame.DataFrame, chart = False) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    data : *pd.DataFrame*
        Dataframe of targeted data

    
* **Returns**

    pd.DataFrame
        Dataframe containing statistics of normality
    