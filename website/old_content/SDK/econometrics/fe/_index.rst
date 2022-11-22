.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
econometrics.fe(
    regression_variables: List[Tuple],
    data: Dict[str, pandas.core.frame.DataFrame],
    entity_effects: bool = False,
    time_effects: bool = False,
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, Any, List[Any], Any]
{{< /highlight >}}

.. raw:: html

    <p>
    When effects are correlated with the regressors the RE and BE estimators are not consistent.
    The usual solution is to use Fixed Effects which are called entity_effects when applied to
    entities and time_effects when applied to the time dimension. [Source: LinearModels]
    </p>

* **Parameters**

    regression_variables : list
        The regressions variables entered where the first variable is
        the dependent variable.
    data : dict
        A dictionary containing the datasets.
    entity_effects : bool
        Whether to include entity effects
    time_effects : bool
        Whether to include time effects

* **Returns**

    The dataset used, the dependent variable, the independent variable and
    the OLS model.
