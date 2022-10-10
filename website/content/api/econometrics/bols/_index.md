## Get underlying data 
### econometrics.bols(regression_variables: List[Tuple], data: Dict[str, pandas.core.frame.DataFrame]) -> Tuple[pandas.core.frame.DataFrame, Any, List[Any], Any]

The between estimator is an alternative, usually less efficient estimator, can can be used to
     estimate model parameters. It is particular simple since it first computes the time averages of
     y and x and then runs a simple regression using these averages. [Source: LinearModels]

    Parameters
    ----------
    regression_variables : list
        The regressions variables entered where the first variable is
        the dependent variable.
    data : dict
        A dictionary containing the datasets.

    Returns
    -------
    The dataset used, the dependent variable, the independent variable and
    the Between OLS model.
