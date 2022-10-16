To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### econometrics.panel(regression_type: str, regression_variables: List[Tuple], data: Dict[str, pandas.core.frame.DataFrame], entity_effects: bool = False, time_effects: bool = False) -> Tuple[pandas.core.frame.DataFrame, Any, List[Any], Any]

Based on the regression type, this function decides what regression to run.

    Parameters
    ----------
    regression_type: str
        The type of regression you wish to execute.
    regression_variables : list
        The regressions variables entered where the first variable is
        the dependent variable.
    data : dict
        A dictionary containing the datasets.
    entity_effects: bool
        Whether to apply Fixed Effects on entities.
    time_effects: bool
        Whether to apply Fixed Effects on time.

    Returns
    -------
    The dataset used, the dependent variable, the independent variable and
    the regression model.

## Getting charts 
### econometrics.panel(data: Dict[str, pandas.core.frame.DataFrame], regression_variables: List[Tuple], regression_type: str = 'OLS', entity_effects: bool = False, time_effects: bool = False, export: str = '', chart=True)

Based on the regression type, this function decides what regression to run.

    Parameters
    ----------
    data : dict
        A dictionary containing the datasets.
    regression_variables : list
        The regressions variables entered where the first variable is
        the dependent variable.
        each column/dataset combination.
    regression_type: str
        The type of regression you wish to execute. Choose from:
        OLS, POLS, RE, BOLS, FE
    entity_effects: bool
        Whether to apply Fixed Effects on entities.
    time_effects: bool
        Whether to apply Fixed Effects on time.
    export : str
        Format to export data

    Returns
    -------
    The dataset used, the dependent variable, the independent variable and
    the regression model.
