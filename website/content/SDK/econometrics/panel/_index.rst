.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Based on the regression type, this function decides what regression to run.
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
econometrics.panel(
    regression\_type: str,
    regression\_variables: List[Tuple],
    data: Dict[str, pandas.core.frame.DataFrame],
    entity\_effects: bool = False,
    time\_effects: bool = False,
    chart: bool = False,
    ) -> Tuple[pandas.core.frame.DataFrame, Any, List[Any], Any]
{{< /highlight >}}

* **Parameters**

    regression\_type: *str*
        The type of regression you wish to execute.
    regression\_variables : *list*
        The regressions variables entered where the first variable is
        the dependent variable.
    data : *dict*
        A dictionary containing the datasets.
    entity\_effects: *bool*
        Whether to apply Fixed Effects on entities.
    time\_effects: *bool*
        Whether to apply Fixed Effects on time.

    
* **Returns**

    The dataset used, the dependent variable, the independent variable and
    the regression model.
    