.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
econometrics.fdols(
    regression_variables: List[Tuple],
    data: Dict[str, pandas.core.frame.DataFrame],
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, Any, List[Any], Any]
{{< /highlight >}}

.. raw:: html

    <p>
    First differencing is an alternative to using fixed effects when there might be correlation.
    When using first differences, time-invariant variables must be excluded. Additionally,
    only one linear time-trending variable can be included since this will look like a constant.
    This variable will soak up all time-trends in the data, and so interpretations of
    these variable can be challenging. [Source: LinearModels]
    </p>

* **Parameters**

    regression_variables : list
        The regressions variables entered where the first variable is
        the dependent variable.
    data : dict
        A dictionary containing the datasets.

* **Returns**

    The dataset used, the dependent variable, the independent variable and
    the OLS model.
