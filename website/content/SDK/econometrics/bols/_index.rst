.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
econometrics.bols(
    regression_variables: List[Tuple],
    data: Dict[str, pandas.core.frame.DataFrame],
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, Any, List[Any], Any]
{{< /highlight >}}

.. raw:: html

    <p>
    The between estimator is an alternative, usually less efficient estimator, can can be used to
     estimate model parameters. It is particular simple since it first computes the time averages of
     y and x and then runs a simple regression using these averages. [Source: LinearModels]
    </p>

* **Parameters**

    regression_variables : list
        The regressions variables entered where the first variable is
        the dependent variable.
    data : dict
        A dictionary containing the datasets.

* **Returns**

    The dataset used, the dependent variable, the independent variable and
    the Between OLS model.
