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
econometrics.root(
    data: pandas.core.series.Series,
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

    data : pd.Series
        Series or column of DataFrame of target variable
    fuller_reg : str
        Type of regression of ADF test
    kpss_reg : str
        Type of regression for KPSS test
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
econometrics.root(
    data: pandas.core.series.Series,
    dataset: str = '',
    column: str = '',
    fuller_reg: str = 'c',
    kpss_reg: str = 'c',
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Determine the normality of a timeseries.
    </p>

* **Parameters**

    data : pd.Series
        Series of target variable
    dataset: str
        Name of the dataset
    column: str
        Name of the column
    fuller_reg : str
        Type of regression of ADF test. Choose c, ct, ctt, or nc
    kpss_reg : str
        Type of regression for KPSS test. Choose c or ct
    export: str
        Format to export data.
    chart: bool
       Flag to display chart

