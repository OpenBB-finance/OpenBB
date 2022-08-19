# alt.oss.repo_summary

To specify a view add `chart=True` as the last parameter

## Model (repo: str)

Get repository summary

    Parameters
    ----------
    repo : str
            Repo to search for Format: org/repo, e.g., openbb-finance/openbbterminal

    Returns
    -------
    pd.DataFrame - Columns: Metric, Value

## View (repo: str, export: str = '') -> None

Display repo summary [Source: https://api.github.com]

    Parameters
    ----------
    repo : str
            Repository to display summary. Format: org/repo, e.g., openbb-finance/openbbterminal
    export : str
        Export dataframe data to csv,json,xlsx file
