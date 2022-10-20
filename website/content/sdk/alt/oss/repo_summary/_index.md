# alt.oss.repo_summary

To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
###alt.oss.repo_summary(repo: str)

Get repository summary

    Parameters
    ----------
    repo : str
            Repo to search for Format: org/repo, e.g., openbb-finance/openbbterminal

    Returns
    -------
    pd.DataFrame - Columns: Metric, Value

## Getting charts 
###alt.oss.repo_summary(repo: str, export: str = '', chart=True) -> None

Display repo summary [Source: https://api.github.com]

    Parameters
    ----------
    repo : str
            Repository to display summary. Format: org/repo, e.g., openbb-finance/openbbterminal
    export : str
        Export dataframe data to csv,json,xlsx file
