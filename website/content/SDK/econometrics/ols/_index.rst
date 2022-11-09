.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
econometrics.ols(
    regression_variables: List[Tuple],
    data: Dict[str, pandas.core.frame.DataFrame],
    show_regression: bool = True,
    export: str = '',
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, Any, List[Any], Any]
{{< /highlight >}}

.. raw:: html

    <p>
    Performs an OLS regression on timeseries data. [Source: Statsmodels]
    </p>

* **Parameters**

    regression_variables : list
        The regressions variables entered where the first variable is
        the dependent variable.
    data : dict
        A dictionary containing the datasets.
    show_regression: bool
        Whether to show the regression results table.
    export: str
        Format to export data

* **Returns**

    The dataset used, the dependent variable, the independent variable and
    the OLS model.
