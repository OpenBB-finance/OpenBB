.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
econometrics.re(
    regression_variables: List[Tuple],
    data: Dict[str, pandas.core.frame.DataFrame],
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, Any, List[Any], Any]
{{< /highlight >}}

.. raw:: html

    <p>
    The random effects model is virtually identical to the pooled OLS model except that is accounts for the
    structure of the model and so is more efficient. Random effects uses a quasi-demeaning strategy which
    subtracts the time average of the within entity values to account for the common shock. [Source: LinearModels]
    </p>

* **Parameters**

    regression_variables : list
        The regressions variables entered where the first variable is
        the dependent variable.
    data : dict
        A dictionary containing the datasets.

* **Returns**

    The dataset used, the dependent variable, the independent variable and
    the RandomEffects model.
