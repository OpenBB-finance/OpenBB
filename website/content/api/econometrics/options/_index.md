To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### econometrics.options(datasets: Dict[str, pandas.core.frame.DataFrame], dataset_name: str = '') -> Dict[Union[str, Any], pandas.core.frame.DataFrame]

Obtain columns-dataset combinations from loaded in datasets that can be used in other commands

    Parameters
    ----------
    datasets: dict
        The available datasets.
    dataset_name: str
        The dataset you wish to show the options for.

    Returns
    -------
    option_tables: dict
        A dictionary with a DataFrame for each option. With dataset_name set, only shows one
        options table.

## Getting charts 
### econometrics.options(datasets: Dict[str, pandas.core.frame.DataFrame], dataset_name: str = None, export: str = '', chart=True)

Plot custom data

    Parameters
    ----------
    datasets: dict
        The loaded in datasets
    dataset_name: str
        The name of the dataset you wish to show options for
    export: str
        Format to export image
