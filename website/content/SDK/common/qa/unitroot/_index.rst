.. role:: python(code)
    :language: python
    :class: highlight

|

To obtain charts, make sure to add :python:`chart = True` as the last parameter.

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
common.qa.unitroot(
    data: pandas.core.frame.DataFrame,
    fuller_reg: str = 'c',
    kpss_reg: str = 'c',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Calculate test statistics for unit roots
    </p>

* **Parameters**

    data : pd.DataFrame
        DataFrame of target variable
    fuller_reg : str
        Type of regression of ADF test. Can be ‘c’,’ct’,’ctt’,’nc’ 'c' - Constant and t - trend order
    kpss_reg : str
        Type of regression for KPSS test.  Can be ‘c’,’ct'
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Dataframe with results of ADF test and KPSS test

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
common.qa.unitroot(
    data: pandas.core.frame.DataFrame,
    target: str,
    fuller_reg: str = 'c',
    kpss_reg: str = 'c',
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Show unit root test calculations
    </p>

* **Parameters**

    data : pd.DataFrame
        DataFrame
    target : str
        Column of data to look at
    fuller_reg : str
        Type of regression of ADF test. Can be ‘c’,’ct’,’ctt’,’nc’ 'c' - Constant and t - trend order
    kpss_reg : str
        Type of regression for KPSS test. Can be ‘c’,’ct'
    export : str
        Format for exporting data
    chart: bool
       Flag to display chart

