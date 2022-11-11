.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
econometrics.pols(
    regression_variables: List[Tuple],
    data: Dict[str, pandas.core.frame.DataFrame],
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, Any, List[Any], Any]
{{< /highlight >}}

.. raw:: html

    <p>
    PooledOLS is just plain OLS that understands that various panel data structures.
    It is useful as a base model. [Source: LinearModels]
    </p>

* **Parameters**

    regression_variables : list
        The regressions variables entered where the first variable is
        the dependent variable.
    data : dict
        A dictionary containing the datasets.

* **Returns**

    The dataset used, the dependent variable, the independent variable and
    the Pooled OLS model.
