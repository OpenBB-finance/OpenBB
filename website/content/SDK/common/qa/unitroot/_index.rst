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
common.qa.unitroot(
    data: pandas.core.frame.DataFrame,
    fuller\_reg: str = 'c',
    kpss\_reg: str = 'c',
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    data : *pd.DataFrame*
        DataFrame of target variable
    fuller_reg : *str*
        Type of regression of ADF test. Can be ‘c’,’ct’,’ctt’,’nc’ 'c' - Constant and t - trend order
    kpss_reg : *str*
        Type of regression for KPSS test.  Can be ‘c’,’ct'

    
* **Returns**

    pd.DataFrame
        Dataframe with results of ADF test and KPSS test
    