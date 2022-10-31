.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Calculate test statistics for unit roots
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
econometrics.root(
    data: pandas.core.series.Series,
    fuller_reg: str = 'c',
    kpss_reg: str = 'c',
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    data : *pd.Series*
        Series or column of DataFrame of target variable
    fuller_reg : *str*
        Type of regression of ADF test
    kpss_reg : *str*
        Type of regression for KPSS test

    
* **Returns**

    pd.DataFrame
        Dataframe with results of ADF test and KPSS test
    