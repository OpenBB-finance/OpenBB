.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Based on the regression type, this function decides what regression to run.
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
econometrics.panel(
    regression_type: str,
    regression_variables: List[Tuple],
    data: Dict[str, pandas.core.frame.DataFrame],
    entity_effects: bool = False,
    time_effects: bool = False,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> Tuple[pandas.core.frame.DataFrame, Any, List[Any], Any]
{{< /highlight >}}

* **Parameters**

    regression_type: *str*
        The type of regression you wish to execute.
    regression_variables : *list*
        The regressions variables entered where the first variable is
        the dependent variable.
    data : *dict*
        A dictionary containing the datasets.
    entity_effects: *bool*
        Whether to apply Fixed Effects on entities.
    time_effects: *bool*
        Whether to apply Fixed Effects on time.
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    The dataset used, the dependent variable, the independent variable and
    the regression model.
