.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
econometrics.get_regression_data(
    regression_variables: List[tuple],
    data: Dict[str, pandas.core.frame.DataFrame],
    regression_type: str = '',
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, Any, List[Any]]
{{< /highlight >}}

.. raw:: html

    <p>
    This function creates a DataFrame with the required regression data as
    well sets up the dependent and independent variables.
    </p>

* **Parameters**

    regression_variables : list
        The regressions variables entered where the first variable is
        the dependent variable.
    data : dict
        A dictionary containing the datasets.
    regression_type: str
        The type of regression that is executed.

* **Returns**

    The dataset used, the dependent variable, the independent variable and
    the OLS model.
