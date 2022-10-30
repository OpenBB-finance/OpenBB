.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > When effects are correlated with the regressors the RE and BE estimators are not consistent.
    The usual solution is to use Fixed Effects which are called entity\_effects when applied to
    entities and time\_effects when applied to the time dimension. [Source: LinearModels]
    </h3>

{{< highlight python >}}
econometrics.fe(
    regression\_variables: List[Tuple],
    data: Dict[str, pandas.core.frame.DataFrame],
    entity\_effects: bool = False,
    time\_effects: bool = False,
    ) -> Tuple[pandas.core.frame.DataFrame, Any, List[Any], Any]
{{< /highlight >}}

* **Parameters**

    regression\_variables : *list*
        The regressions variables entered where the first variable is
        the dependent variable.
    data : *dict*
        A dictionary containing the datasets.
    entity\_effects : *bool*
        Whether to include entity effects
    time\_effects : *bool*
        Whether to include time effects

    
* **Returns**

    The dataset used, the dependent variable, the independent variable and
    the OLS model.
    